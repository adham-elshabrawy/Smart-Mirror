import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.svm import SVC
import os
from glob import glob

#Load and resize images from a folder for now
def images_from_folder(folder):
    images = []
    labels = []
    for label_folder in os.listdir(folder): #Different subfolders for each class
        class_folder = os.path.join(folder, label_folder)
        if os.path.isdir(class_folder):
            for filename in glob(f"{class_folder}/*.jpg"):
                img = cv2.imread(filename) 
                if img is not None:
                    img = cv2.resize(img, (128,128))
                    images.append(img)
                    labels.append(label_folder)
    return np.array(images), np.array(labels) #numpy array to be easier processed


#Extract features using HOG decriptors (Captures shape and structure of objects)
def extract_features(images):
    hog = cv2.HOGDescriptor()
    features = [hog.compute(img) for img in images]
    return np.array(features, dtype=np.float32)

#Train SVM classifier for now, look into optimization later
def train_classifier(features, labels):
    classifier = SVC(kernel='linear', probability=True)
    classifier.fit(features, labels)
    return classifier

#Classify an image
def classify_image(classifier, img):
    hog = cv2.HOGDescriptor()
    feature = hog.compute(cv2.resize(img, (128,128))).reshape(1,-1) #Reshapes the feature array to match input expected
    prediction = classifier.predict(feature)
    return prediction[0]


if __name__ == "__main__":
    dataset_path = "path/to/data" #INSERT DATASET PATH HERE ONCE FOUND
    images, labels = images_from_folder(dataset_path)

    features = extract_features(images)
    classifier = train_classifier(features, labels)

    test_img_path = "path to test image" #REPLACE WITH A TEST IMAGE PATH
    test_img = cv2.imread(test_img_path)
    prediction = classify_image(classifier, test_img)

    print(f"Predicted class: {prediction}")
