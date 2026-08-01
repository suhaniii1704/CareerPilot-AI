from pathlib import Path


def save_resume(uploaded_file, upload_dir):
    """
    Save the uploaded resume to the uploads folder.

    Parameters:
        uploaded_file : UploadedFile
            File received from Streamlit.
        upload_dir : Path
            Path to the uploads directory.

    Returns:
        Path
            Path of the saved resume.
    """

    # Create uploads folder if it doesn't exist
    upload_dir.mkdir(exist_ok=True)

    # Create full file path
    save_path = upload_dir / uploaded_file.name

    # Save file in binary mode
    with open(save_path, "wb") as file:
        file.write(uploaded_file.getbuffer())

    return save_path