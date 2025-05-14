def is_director(request):
    if request.user.is_authenticated:
        return {
            "is_director": request.user.roles.filter(role__name="Директор").exists()
        }
    return {"is_director": False}
