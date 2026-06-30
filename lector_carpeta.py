def leer_carpeta(service):
    resultado = (
        service.spreadsheets()
        .values()
        .files()
        .execute()
    )

    return resultado.get("values", [])