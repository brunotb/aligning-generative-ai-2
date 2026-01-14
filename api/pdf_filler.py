import json
import os

def fill_anmeldung_form(
    full_name: str,
    date_of_birth: str,
    nationality: str,
    move_in_date: str,
    new_address_street: str,
    new_address_zip: str,
    new_address_city: str,
    previous_address: str
):
    """
    Fills the Munich Residence Registration (Anmeldung) form.
    
    Args:
        full_name: The full name of the person.
        date_of_birth: Date of birth (DD.MM.YYYY).
        nationality: Nationality (e.g., Italian).
        move_in_date: Date of moving in (DD.MM.YYYY).
        new_address_street: Street and House Number of the new apartment.
        new_address_zip: Logal ZIP code.
        new_address_city: City name.
        previous_address: Full address of the previous residence.
    """
    
    data = {
        "full_name": full_name,
        "date_of_birth": date_of_birth,
        "nationality": nationality,
        "move_in_date": move_in_date,
        "new_address_street": new_address_street,
        "new_address_zip": new_address_zip,
        "new_address_city": new_address_city,
        "previous_address": previous_address
    }
    
    # In a real app, we would use pypdf to fill the form.
    # For this prototype, we will save the data to a JSON file to verify it worked.
    
    # Use /tmp for serverless environments (like Vercel) where other paths are read-only
    output_dir = "/tmp"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{output_dir}/anmeldung_{full_name.replace(' ', '_')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return f"Successfully filled the form for {full_name}. Data saved to {filename}."
