import base64
import uuid


class ImagePathsGenerator:
    @staticmethod
    def _generate_pseudo_id(amount_of_iterations: int = 3) -> str:
        if amount_of_iterations <= 0:
            raise ValueError(f'Please provide positive amount of iterations. Current: "{amount_of_iterations}"')

        return (
            base64.urlsafe_b64encode(b"".join(uuid.uuid4().bytes for _ in range(amount_of_iterations)))
            .decode()
            .replace("=", "")
        )

    @staticmethod
    def get_user_avatar_path(instance, avatar: str):
        _, extension = avatar.rsplit(".", maxsplit=1)
        return (
            f"users/user/avatar/"
            f"{ImagePathsGenerator._generate_pseudo_id(amount_of_iterations=4)}/"
            f"{ImagePathsGenerator._generate_pseudo_id(amount_of_iterations=1)}/"
            f"avatar.{extension}"
        )

    @staticmethod
    def get_company_logo(instance, logo: str):
        _, extension = logo.rsplit(".", maxsplit=1)
        return (
            f"companies/company/logo/"
            f"{ImagePathsGenerator._generate_pseudo_id(amount_of_iterations=4)}/"
            f"{ImagePathsGenerator._generate_pseudo_id(amount_of_iterations=1)}/"
            f"logo.{extension}"
        )
