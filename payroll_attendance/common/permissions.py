def is_admin_or_same_branch(user, branch_id):
    """Return whether an admin is global or a manager owns the branch."""
    return user.rol == "admin_general" or (
        user.rol == "gerente_sucursal" and branch_id == user.sucursal_id
    )
