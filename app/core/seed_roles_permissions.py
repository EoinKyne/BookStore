from sqlalchemy.orm import Session
from BookStore.app.models.model import Role as UserRole
from BookStore.app.models.model import Permission as UserPermission


def seed_roles(db: Session):

    perms = [
        "book:create",
        "book:update",
        "book:delete",
        "book:purchase",
        "admin:full",
    ]

    permission_objs = {}

    for name in perms:
        perm = db.query(UserPermission).filter_by(name=name).first()
        if not perm:
            perm = UserPermission(name=name)
            db.add_all(permission_objs.values())
            db.flush()
        permission_objs[name] = perm

    superuser_role = db.query(UserRole).filter_by(name="Administrator").first()
    if not superuser_role:
        superuser_role = UserRole(
            name = "Administrator",
            permissions=list(permission_objs.values())
        )
        db.add(superuser_role)
    else:
        superuser_role.permissions = list(permission_objs.values())

    contributor_role = db.query(UserRole).filter_by(name="Contributor").first()
    if not contributor_role:
        contributor_role = UserRole(
            name="Contributor",
            permissions=[
                permission_objs["book:create"],
                permission_objs["book:update"],
                permission_objs["book:delete"]
            ]
        )
        db.add(contributor_role)
    else:
        contributor_role.permissions = list(permission_objs.values())

    db.commit()

