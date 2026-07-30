with open("noisekey_package.bin", "rb") as f:
    loaded_package = f.read()
    print("Loaded launch Package:", loaded_package)
    print("launch Package loaded successfully.")
    print("total package length:", len(loaded_package))
    print("Loading complete.")
