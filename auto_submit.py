import random
import time
import urllib.parse
import requests
import numpy as np

# Base Form Submission URL
BASE_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdmLmtT3qjkuyBC2TPn0-nRdFCXHbbF64nVB3fCkdGgeaaVbQ/formResponse"
TOTAL_RESPONSES = 2

# --- TYPO & INFORMAL TEXT ENGINE ---

def introduce_human_typos(text):
    """Applies realistic human typing errors: letter swaps, shortcuts, casing."""
    substitutions = {
        "please": ["pls", "pleese", "plz"],
        "payment": ["paymnet", "pamnt", "paymet"],
        "transaction": ["transaction", "tranzaction", "tranasction"],
        "charge": ["chrage", "chrge", "charget"],
        "charges": ["chrges", "chrages"],
        "service": ["servise", "srvice"],
        "problem": ["problm", "prblem"],
        "system": ["sistem", "system"],
        "network": ["netwrk", "netwok"],
        "slow": ["slw", "sloooow"],
        "internet": ["itnernet", "intrnet"],
        "bank": ["bank", "bakn"]
    }

    words = text.split()
    new_words = []

    for word in words:
        clean_word = word.lower().strip(".,")
        
        # 25% chance to substitute with a misspelled/shortened word
        if clean_word in substitutions and random.random() < 0.25:
            replacement = random.choice(substitutions[clean_word])
            new_words.append(replacement)
            continue

        # 10% chance to swap adjacent letters inside words longer than 4 chars
        if len(word) > 4 and random.random() < 0.10:
            idx = random.randint(1, len(word) - 2)
            word_list = list(word)
            word_list[idx], word_list[idx+1] = word_list[idx+1], word_list[idx]
            word = "".join(word_list)

        new_words.append(word)

    result = " ".join(new_words)

    # 45% chance to convert entire response to lowercase
    if random.random() < 0.45:
        result = result.lower()

    # 35% chance to strip ending period
    if random.random() < 0.35 and result.endswith("."):
        result = result[:-1]

    return result

def generate_unique_correlated_suggestion(sec_d_scores, biz_type):
    """
    Dynamically constructs a 100% unique suggestion that directly 
    correlates with the respondent's highest rated challenge in Section 4.
    """
    highest_challenge = max(sec_d_scores, key=lambda k: int(sec_d_scores[k]))
    openers = ["Please", "Pls", "Need to", "Government and banks should", "Kindly", "Requesting to", "Must", "Good if they"]

    if highest_challenge == "entry.302692740":  # High Transaction Fees
        actions = ["reduce", "lower", "minimize", "cut down", "remove"]
        subjects = ["MDR transaction charges", "QR code fee", "bank commission rates", "digital service charges"]
        contexts = [f"for small {biz_type.lower()} shops", "for daily transactions under 1000 NRS", "for retail merchants", "to support small businesses"]
        closings = ["pls", "as soon as possible", "it hurts small profit margins", "which is currently too high", ""]

    elif highest_challenge == "entry.853618079":  # Poor Internet
        actions = ["improve", "upgrade", "stabilize", "boost", "fix"]
        subjects = ["internet connectivity", "mobile network speed", "server connection", "Wi-Fi coverage"]
        contexts = ["in local market areas", "during peak shopping hours", "for quick QR scanning", "near retail hubs"]
        closings = ["payment gets stuck often", "customers have to wait long", "very annoying during rush hour", ""]

    elif highest_challenge == "entry.1261505465":  # Error Resolution / Refunds
        actions = ["speed up", "fast track", "simplify", "fix"]
        subjects = ["refund processing time", "dispute resolution", "failed transaction reversal", "bank customer support"]
        contexts = ["when payment fails", "for pending transactions", "with 24/7 support hotline", "within 24 hours max"]
        closings = ["currently takes 2-3 days", "money gets stuck and customers complain", "it breaks trust", ""]

    elif highest_challenge == "entry.1929323042":  # Customer Unawareness
        actions = ["conduct", "launch", "provide", "increase"]
        subjects = ["awareness campaigns", "customer education", "training programs", "simple user guides"]
        contexts = ["for older customers", "about scanning QR codes safely", "in local markets", "for non-tech-savvy shoppers"]
        closings = ["many still prefer cash", "they don't know how to use digital wallets", ""]

    else:  # Technical Knowledge / General
        actions = ["make", "provide", "design", "offer"]
        subjects = ["simpler mobile banking apps", "free QR display stands", "merchant training sessions", "easier app interfaces"]
        contexts = [f"for new {biz_type.lower()} owners", "with local language support", "for small shopkeepers", ""]
        closings = ["to make it easy for everyone", "to encourage digital adoption", ""]

    parts = [
        random.choice(openers),
        random.choice(actions),
        random.choice(subjects),
        random.choice(contexts),
        random.choice(closings)
    ]
    
    raw_sentence = " ".join([p for p in parts if p]).strip()
    return introduce_human_typos(raw_sentence)

def sample_likert(mean, std_dev=0.8, introduce_item_noise=False):
    """Samples Likert 1-5 score using normal distribution + optional item noise."""
    if introduce_item_noise and random.random() < 0.10:
        val = 6.0 - np.random.normal(mean, std_dev)
    else:
        val = np.random.normal(mean, std_dev)
    return str(int(np.clip(round(val), 1, 5)))

# --- SUBMISSION LOOP (2 RESPONSES PER HOURLY RUN) ---

used_suggestions = set()

print(f"Starting execution for {TOTAL_RESPONSES} scheduled responses...\n")

for i in range(1, TOTAL_RESPONSES + 1):
    # Random Pre-Submission Waiting Delays for Random Timestamps:
    # Response #1 waits a random 1 to 15 minutes
    # Response #2 waits another random 10 to 30 minutes
    if i == 1:
        wait_seconds = random.uniform(60, 900)   # 1 to 15 minutes
    else:
        wait_seconds = random.uniform(600, 1800) # 10 to 30 minutes

    print(f"[{i}/{TOTAL_RESPONSES}] Waiting {round(wait_seconds / 60, 1)} minutes before submitting at a random minute...")
    time.sleep(wait_seconds)

    # Select Archetype
    archetype = random.choices(
        ["Standard_TechSavvy", "Standard_Traditional", "Standard_Moderate", 
         "Outlier_OlderEnthusiast", "Outlier_SkepticalYouth", "Outlier_SelfTaughtHighAdopter"],
        weights=[0.35, 0.25, 0.17, 0.08, 0.08, 0.07]
    )[0]

    if archetype == "Outlier_OlderEnthusiast":
        gender, age, edu = random.choice(["Male", "Female"]), random.choice(["40-49", "50 and above"]), random.choice(["School level", "No formal education"])
        biz, years, accept_digital, methods = random.choice(["Grocery", "Pharmacy"]), "More than 5 years", "Yes", ["QR code", "eSewa"]
        duration, pct, base_satisfaction, base_friction = "More than 2 years", random.choice(["61–80%", "81–100%"]), 4.4, 2.1

    elif archetype == "Outlier_SkepticalYouth":
        gender, age, edu = random.choice(["Male", "Female"]), "20-29", "Bachelor's or above"
        biz, years, accept_digital, methods = random.choice(["Electronics", "Restaurant and Cafe"]), "1-3 years", "Yes", random.sample(["Khalti", "ConnectIPS", "Mobile Banking"], k=2)
        duration, pct, base_satisfaction, base_friction = "1–2 years", random.choice(["21–40%", "41–60%"]), 2.2, 4.1

    elif archetype == "Outlier_SelfTaughtHighAdopter":
        gender, age, edu = "Male", random.choice(["30-39", "40-49"]), random.choice(["No formal education", "School level"])
        biz, years, accept_digital, methods = "Grocery", "3-5 years", "Yes", ["QR code", "Mobile Banking"]
        duration, pct, base_satisfaction, base_friction = "1–2 years", random.choice(["61–80%", "81–100%"]), 4.0, 2.5

    elif archetype == "Standard_TechSavvy":
        gender, age, edu = random.choices(["Male", "Female"], weights=[0.6, 0.4])[0], random.choices(["20-29", "30-39"], weights=[0.6, 0.4])[0], "Bachelor's or above"
        biz, years, accept_digital = random.choice(["Electronics", "Restaurant and Cafe", "Clothing and Apparel"]), random.choice(["1-3 years", "Less than 1 year"]), "Yes"
        methods, duration, pct = random.sample(["eSewa", "QR code", "Mobile Banking"], k=random.randint(2, 3)), random.choice(["1–2 years", "More than 2 years"]), random.choice(["41–60%", "61–80%"])
        base_satisfaction, base_friction = 4.1, 2.2

    elif archetype == "Standard_Traditional":
        gender, age, edu = random.choices(["Male", "Female"], weights=[0.7, 0.3])[0], random.choices(["40-49", "50 and above"], weights=[0.5, 0.5])[0], random.choices(["School level", "Intermediate"], weights=[0.6, 0.4])[0]
        biz, years, accept_digital = "Grocery", "More than 5 years", random.choices(["Yes", "No"], weights=[0.7, 0.3])[0]
        methods, duration, pct = ["QR code"], "Less than 6 months", random.choice(["0–20%", "21–40%"])
        base_satisfaction, base_friction = 2.8, 3.9

    else:  # Standard_Moderate
        gender, age, edu = random.choice(["Male", "Female"]), random.choice(["20-29", "30-39", "40-49"]), "Intermediate"
        biz, years, accept_digital = random.choice(["Grocery", "Clothing and Apparel", "Pharmacy"]), random.choice(["1-3 years", "3-5 years"]), "Yes"
        methods, duration, pct = random.sample(["eSewa", "QR code"], k=random.randint(1, 2)), random.choice(["6 months–1 year", "1–2 years"]), random.choice(["21–40%", "41–60%"])
        base_satisfaction, base_friction = 3.5, 3.0

    # Section 4 Likert Challenge Scores
    sec_d_scores = {
        "entry.769010039":  sample_likert(base_friction),                          # Tech knowledge
        "entry.853618079":  sample_likert(base_friction + 0.2, introduce_item_noise=True), # Internet
        "entry.302692740":  sample_likert(base_friction + 0.5),                    # Fees (Universal)
        "entry.1261505465": sample_likert(base_friction + 0.1),                    # Errors/Refunds
        "entry.440890793":  sample_likert(base_friction - 0.2),                    # Security
        "entry.1929323042": sample_likert(base_friction, introduce_item_noise=True),# Unawareness
        "entry.262712549":  sample_likert(base_friction + 0.1)                     # Settlement
    }

    # Generate 100% Unique Suggestion Correlated to Section 4
    suggestion = generate_unique_correlated_suggestion(sec_d_scores, biz)
    while suggestion in used_suggestions:
        suggestion = generate_unique_correlated_suggestion(sec_d_scores, biz)
    used_suggestions.add(suggestion)

    # Build Payload for HTTP POST Request
    payload = {
        # Section 1
        "entry.2032045283": gender,
        "entry.1972684812": age,
        "entry.1917844224": edu,
        "entry.1934597270": biz,
        "entry.1835522301": years,

        # Section 2
        "entry.1462473244": accept_digital,
        "entry.1016455579": methods,  # List for checkboxes
        "entry.1411040558": duration,
        "entry.1976167213": pct,

        # Section 3 Likert
        "entry.1780399034": sample_likert(base_satisfaction, introduce_item_noise=True),
        "entry.2100266447": sample_likert(base_satisfaction + 0.1),
        "entry.789230503":  sample_likert(base_satisfaction - 0.1, introduce_item_noise=True),
        "entry.415001109":  sample_likert(base_satisfaction - 0.2),
        "entry.1020046730": sample_likert(base_satisfaction + 0.2),
        "entry.1240134955": sample_likert(base_satisfaction - 0.3),
        "entry.699940555":  sample_likert(base_satisfaction - 0.1),
        "entry.940936041":  sample_likert(base_satisfaction),

        # Section 4 Likert
        **sec_d_scores,

        # Unique Suggestion
        "entry.1432289954": suggestion,

        # Page metadata
        "pageHistory": "0,1,2,3",
        "submit": "Submit"
    }

    # Send Live HTTP POST Request
    try:
        res = requests.post(BASE_URL, data=payload, timeout=10)
        if res.status_code == 200:
            print(f"[{i}/{TOTAL_RESPONSES}] Submitted ({archetype}) -> Suggestion: \"{suggestion}\"")
        else:
            print(f"[{i}/{TOTAL_RESPONSES}] Failed with HTTP Status Code: {res.status_code}")
    except Exception as e:
        print(f"[{i}/{TOTAL_RESPONSES}] Network Error: {e}")

print("\nHourly run finished! 2 responses submitted at random minutes.")
