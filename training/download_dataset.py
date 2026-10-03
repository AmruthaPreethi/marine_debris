import kagglehub

path = kagglehub.dataset_download(
    "mawins/side-scan-sonar-image-for-object-detection"
)

print("Dataset downloaded to:")
print(path)