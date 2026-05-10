from tiktok_uploader.upload import upload_video

upload_video(
    filename='frutinovela_video1.mp4',
    description='Mi primer video #viral',
    headless=False,  # No se cierra, podés ver qué pasa
    cookies='cookies.txt'
)