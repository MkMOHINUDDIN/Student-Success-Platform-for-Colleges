def explain_student(feats, coefficients, feature_names, top_k=4):
    rows = []
    for name, coef in zip(feature_names, coefficients):
        value = feats.get(name, 0)
        direction = "increases risk" if coef > 0 else "decreases risk"
        contribution = float(coef) * float(value)
        rows.append({
            "feature": name,
            "value": value,
            "coefficient": round(float(coef), 4),
            "direction": direction,
            "signed_contribution": round(contribution, 4),
        })
    rows.sort(key=lambda r: abs(r["signed_contribution"]), reverse=True)
    return {"insufficient_data": False, "factors": rows[:top_k]}
