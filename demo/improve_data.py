import json

# Load your predictions
with open("pred_improve_data.json", "r") as f:
    data = json.load(f)

# Try a range of thresholds
best_accuracy = 0
best_thresholds = (None, None)
results = []

# Sweep centrist bounds from -0.4 to 0.4 in 0.01 steps
for low in [round(x * 0.001, 3) for x in range(-400, 0)]:
    for high in [round(x * 0.001, 3) for x in range(1, 401)]:
        correct = 0
        for item in data:
            score = item["predicted_raw"]
            true = item["stance"]

            # Apply thresholds
            if low <= score <= high:
                pred = "Centrist"
            elif score < low:
                pred = "Liberal"
            else:
                pred = "Conservative"

            if pred == true:
                correct += 1

        acc = correct / len(data)
        results.append((low, high, acc))
        if acc > best_accuracy:
            best_accuracy = acc
            best_thresholds = (low, high)

# Show best
print(f"\n✅ Best accuracy: {best_accuracy:.2%}")
print(f"   Best thresholds: Liberal if < {best_thresholds[0]}, Conservative if > {best_thresholds[1]}, else Centrist")

# Optional: top 5
top_5 = sorted(results, key=lambda x: x[2], reverse=True)[:5]
print("\nTop 5 threshold combos:")
for low, high, acc in top_5:
    print(f"Centrist range: {low} to {high} → Accuracy: {acc:.2%}")
