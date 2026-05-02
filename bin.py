with open("receive.bin", "rb") as f:
    loaded_package = f.read()
    print("Loaded receive Package:", loaded_package)
    print("receive Package loaded successfully.")
    print("total package length:", len(loaded_package))
    print("Loading complete.")
