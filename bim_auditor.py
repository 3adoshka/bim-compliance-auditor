import sys
import ifcopenshell
import pandas as pd

def audit_bim_model(ifc_file_path: str):
    print(f"[*] Ingesting BIM model for compliance audit: {ifc_file_path}...")
    try:
        model = ifcopenshell.open(ifc_file_path)
    except Exception as e:
        print(f"[!] Critical Error: Could not parse IFC file. Details: {e}")
        sys.exit(1)

    # Extract all physical products (Walls, Slabs, Doors, Columns, etc.)
    elements = model.by_type("IfcProduct")
    audit_records = []

    print(f"[*] Auditing {len(elements)} elements against project data standards...")

    for elem in elements:
        # Skip spatial containers
        if elem.is_a() in ["IfcSite", "IfcBuilding", "IfcBuildingStorey"]:
            continue

        global_id = getattr(elem, "GlobalId", "N/A")
        name = getattr(elem, "Name", "Unnamed Element")
        element_type = elem.is_a()

        # Real-world check: Does the element have a valid name and GlobalId?
        has_valid_name = 1 if name and name != "Unnamed Element" else 0
        
        # Check if the element contains property sets (simulating mandatory BIM execution plan checks)
        has_psets = 1 if hasattr(elem, "IsDefinedBy") and len(elem.IsDefinedBy) > 0 else 0

        audit_records.append({
            "GlobalId": global_id,
            "ElementType": element_type,
            "ElementName": name,
            "HasValidName": has_valid_name,
            "HasPropertySets": has_psets
        })

    df = pd.DataFrame(audit_records)
    
    if df.empty:
        print("[!] Warning: No physical elements found to audit.")
        return

    # Compute Compliance Metrics
    total_elements = len(df)
    compliant_elements = df[(df["HasValidName"] == 1) & (df["HasPropertySets"] == 1)]
    compliance_score = (len(compliant_elements) / total_elements) * 100

    print("\n" + "="*70)
    print(" BIM MODEL COMPLIANCE & DATA GOVERNANCE AUDIT REPORT")
    print("="*70)
    print(f"Total Elements Audited : {total_elements}")
    print(f"Fully Compliant Assets : {len(compliant_elements)}")
    print(f"Model Compliance Score : {compliance_score:.2f}%")
    print("="*70)

    # Export exception log for non-compliant elements
    non_compliant_df = df[(df["HasValidName"] == 0) | (df["HasPropertySets"] == 0)]
    output_log = "bim_compliance_exceptions.csv"
    non_compliant_df.to_csv(output_log, index=False)
    
    print(f"\n[SUCCESS] Exception log exported to '{output_log}' for subcontractor correction.")

if __name__ == "__main__":
    # Use our local test file or accept CLI argument
    target = sys.argv[1] if len(sys.argv) > 1 else "sample_model.ifc"
    audit_bim_model(target)
