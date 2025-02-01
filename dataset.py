import kagglehub

# Download latest version
path = kagglehub.dataset_download("henryshan/student-performance-prediction")

print("Path to dataset files:", path)