from PyPDFForm import PdfWrapper

# Load the PDF (Ensure the path is correct for your environment)
pdf = PdfWrapper("data/Anmeldung_Meldeschein_20220622.pdf", use_full_widget_name=True)

# ---------------------------------------------------------
# VALIDATED DATASET: "The International Family"
# Scenario: A married couple with a child moving from Brazil.
# Person 1: German/Brazilian (Dual Citizen), Doctor, Noble Name.
# Person 2: German, Different Surname, Protestant.
# Person 3: Child, Diverse Gender, Double-barrel surname.
# ---------------------------------------------------------

validated_data = {
    # --- SECTION 1: MOVE DETAILS ---
    # Validation: Standard German Date Format DD.MM.YYYY
    "einzug": "15.01.25",
    
    # Validation: Full address including floor/apt for precise identification
    "neuw.strasse": "Leopoldstraße 25 a, 3. Stock",
    "nw.plz": "80802",
    
    # Validation: Widget 'wohnung' is a Radio Group (0-based index)
    # Options: [0] Alleinige, [1] Haupt, [2] Neben
    # Rule: If this is their only German home, it is "Alleinige" (0).
    "wohnung": 0, 

    # --- SECTION 2: PREVIOUS ADDRESS (The "Abroad" Rule) ---
    # Rule: If moving from abroad, fill 'zuzug'. Leave 'bishwo' (previous German address) blank 
    # unless reporting a return to a previous German home.
    "zuzug": "Torstraße 208, 10115 Berlin, Deutschland",
    "bishwo.strasse": "Rua Augusta 1500",
    "bishwo.plz": "01304-001",
    "bishwo.ort": "São Paulo, Brasilien",

    # --- SECTION 3: PERSON 1 (The Applicant) ---
    "fam1": "von Gräfenberg",        # Noble prefix belongs in Family Name
    "vorn1": "Maria-Luisa",          # Hyphenated names are valid
    
    # Validation: Academic degrees go here, NOT in 'vorn1'
    "gr1": "Dr.",
    
    # Validation: Radio Index for Gender [0=M, 1=W, 2=oA, 3=D]
    "geschl1": 1,                    # Female
    
    # Validation: Radio Index for Family Status (Page 4 key)
    # [0=LD, 1=VH, 2=VW, 3=GS, 4=LP...]
    "famst1": 1,                     # Married (VH)
    
    # Validation: Radio Index for Religion (Page 4 key)
    # [0=rk, 1=ak ... 8=ev]
    "rel1": 0,                       # Roman Catholic
    
    # Validation: Multiple nationalities allowed
    "staatsang1": "Deutsch, Brasilianisch",
    
    # Validation: Marriage data required if status is VH
    "dat1": "10.08.2015, Rom",

    # --- SECTION 4: PERSON 2 (The Spouse) ---
    # Scenario: Spouse kept birth name (Name Change Logic)
    "fam2": "Müller",
    "vorn2": "Hans-Peter",
    "gr2": "",                       # No title
    "geschl2": 0,                    # Male
    "famst2": 1,                     # Married (Must match P1)
    
    # Validation: Mixed Religion Marriage
    "rel2": 8,                       # Evangelisch (Protestant)
    "staatsang2": "Deutsch",
    "dat2": "10.08.2015, Rom",       # Must match P1

    # --- SECTION 5: PERSON 3 (The Child) ---
    # Scenario: Double-barrel name, diverse gender
    "fam3": "Müller-Gräfenberg",
    "vorn3": "Alex",
    "gebdat3": "01.01.2015",
    "gebort3": "São Paulo",
    
    # Validation: Gender "Divers" (Index 3 on Page 4)
    "geschl3": 3,
    "famst3": 0,                     # Single (LD)
    
    # Validation: Religion "None" (oa)
    # Index calculation: rk(0)..ev(8)..oa is usually the last one (~21 or 22)
    "rel3": 21,                      # oa (Ohne Angabe / None)
    "staatsang3": "Brasilianisch",

    # --- SECTION 6: PASSPORTS (ID Types) ---
    # Validation: Types mapped from Page 4 [0=PA, 1=RP, 2=KRP...]
    
    # Person 1: Personalausweis (PA)
    "art1": 0,
    "serien1": "L01X00T47",
    "ausstellb1": "Stadt Berlin",
    "ausstelldat1": "15.05.2020",
    "gueltig1": "14.05.2030",

    # Person 2: Reisepass (RP)
    "art2": 1,
    "serien2": "C34567891",
    "ausstellb2": "KVR München",
    "ausstelldat2": "01.02.2019",
    "gueltig2": "31.01.2029",

    # --- SECTION 7: SEPARATION CHECK ---
    # Bottom of Page 1: "Leben Sie dauerhaft getrennt...?"
    # Options: [0] Ja, [1] Nein
    # Logic: Moving in together -> Nein.
    "getrennt1": 1,

    # --- SECTION 8: SIGNATURE ---
    "Ort1": "München",
    "Datum1": "15.01.2025"
}

# Fill the PDF
filled_pdf = pdf.fill(validated_data)

# Save output
output_filename = "output//Anmeldung_Meldeschein_filled.pdf"
filled_pdf.write(output_filename)
print(f"PDF Successfully generated: {output_filename}")
