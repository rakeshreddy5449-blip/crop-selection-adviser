
import joblib
import tensorflow as tf
import os

print("Checking crop recommendation models...\n")

try:
    rf = joblib.load("models/random_forest_model.joblib")
    print("1. Random Forest: LOADED")

    svm = joblib.load("models/svm_model.joblib")
    print("2. SVM: LOADED")

    scaler = joblib.load("models/ann_scaler.joblib")
    print("3. ANN Scaler: LOADED")

    encoder = joblib.load("models/label_encoder.joblib")
    print("4. Label Encoder: LOADED")

    ann = tf.keras.models.load_model("models/ann_crop_model.keras")
    print("5. ANN Model: LOADED")

    print("\nANN Input Shape:", ann.input_shape)
    print("ANN Output Shape:", ann.output_shape)
    print("Number of crop classes:", len(encoder.classes_))

    print("\nSUCCESS: All models loaded correctly!")

except Exception as e:
    print("\nMODEL LOADING FAILED:")
    print(type(e).__name__, "-", e)
