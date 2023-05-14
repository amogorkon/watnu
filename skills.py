from collections import defaultdict
from enum import Enum
from typing import NamedTuple


class Skill(NamedTuple):
    name: str
    icon: str | None
    description: str
    description_de: str | None = None
    description_es: str | None = None

    # def __new__(cls, **kwargs):
    #     if not kwargs:
    #         raise TypeError(f"{cls.__name__}() takes keyword arguments only")
    #     return super().__new__(cls, **kwargs)


class Skills(Enum):
    reading = Skill(
        "Reading",
        None,
        "The ability to read and understand written text.",
    )
    writing = Skill(
        name="Writing", icon=None, description="The ability to write and communicate ideas in written form."
    )
    speaking = Skill("Speaking", None, "The ability to speak and communicate ideas in spoken form.")
    listening = Skill("Listening", None, "The ability to listen and understand spoken language.")
    math = Skill("Math", None, "The ability to understand and apply mathematical concepts.")
    science = Skill("Science", None, "The ability to understand and apply scientific concepts.")
    history = Skill("History", None, "The ability to understand and apply historical concepts.")
    geography = Skill("Geography", None, "The ability to understand and apply geographical concepts.")
    programming = Skill("Programming", None, "The ability to understand and apply programming concepts.")
    art = Skill("Art", None, "The ability to understand and apply artistic concepts.")
    music = Skill("Music", None, "The ability to understand and apply musical concepts.")
    physical_education = Skill(
        "Physical Education", None, "The ability to understand and apply physical education concepts."
    )
    health = Skill("Health", None, "The ability to understand and apply health concepts.")
    social_studies = Skill(
        "Social Studies", None, "The ability to understand and apply social studies concepts."
    )
    foreign_language = Skill(
        "Foreign Language", None, "The ability to understand and apply foreign language concepts."
    )
    computer_science = Skill(
        "Computer Science", None, "The ability to understand and apply computer science concepts."
    )
    engineering = Skill("Engineering", None, "The ability to understand and apply engineering concepts.")
    business = Skill("Business", None, "The ability to understand and apply business concepts.")
    economics = Skill("Economics", None, "The ability to understand and apply economic concepts.")
    politics = Skill("Politics", None, "The ability to understand and apply political concepts.")
    law = Skill("Law", None, "The ability to understand and apply legal concepts.")
    philosophy = Skill("Philosophy", None, "The ability to understand and apply philosophical concepts.")
    psychology = Skill("Psychology", None, "The ability to understand and apply psychological concepts.")
    sociology = Skill("Sociology", None, "The ability to understand and apply sociological concepts.")
    anthropology = Skill(
        "Anthropology", None, "The ability to understand and apply anthropological concepts."
    )
    archaeology = Skill("Archaeology", None, "The ability to understand and apply archaeological concepts.")
    theology = Skill("Theology", None, "The ability to understand and apply theological concepts.")
    agriculture = Skill("Agriculture", None, "The ability to understand and apply agricultural concepts.")
    cooking = Skill("Cooking", None, "The ability to understand and apply cooking concepts.")
    carpentry = Skill("Carpentry", None, "The ability to understand and apply carpentry concepts.")
    plumbing = Skill("Plumbing", None, "The ability to understand and apply plumbing concepts.")
    electrical = Skill("Electrical", None, "The ability to understand and apply electrical concepts.")
    mechanical = Skill("Mechanical", None, "The ability to understand and apply mechanical concepts.")
    automotive = Skill("Automotive", None, "The ability to understand and apply automotive concepts.")
    masonry = Skill("Masonry", None, "The ability to understand and apply masonry concepts.")
    welding = Skill("Welding", None, "The ability to understand and apply welding concepts.")
    metalworking = Skill("Metalworking", None, "The ability to understand and apply metalworking concepts.")
    mining = Skill("Mining", None, "The ability to understand and apply mining concepts.")
    hunting = Skill("Hunting", None, "The ability to understand and apply hunting concepts.")
    fishing = Skill("Fishing", None, "The ability to understand and apply fishing concepts.")
    farming = Skill("Farming", None, "The ability to understand and apply farming concepts.")
    ranching = Skill("Ranching", None, "The ability to understand and apply ranching concepts.")
    animal_husbandry = Skill(
        "Animal Husbandry", None, "The ability to understand and apply animal husbandry concepts."
    )
    animal_training = Skill(
        "Animal Training", None, "The ability to understand and apply animal training concepts."
    )
    animal_grooming = Skill(
        "Animal Grooming", None, "The ability to understand and apply animal grooming concepts."
    )
    animal_breeding = Skill(
        "Animal Breeding", None, "The ability to understand and apply animal breeding concepts."
    )
    animal_care = Skill("Animal Care", None, "The ability to understand and apply animal care concepts.")
    animal_feeding = Skill(
        "Animal Feeding", None, "The ability to understand and apply animal feeding concepts."
    )
    animal_health = Skill(
        "Animal Health", None, "The ability to understand and apply animal health concepts."
    )
    animal_nutrition = Skill(
        "Animal Nutrition", None, "The ability to understand and apply animal nutrition concepts."
    )
    animal_behavior = Skill(
        "Animal Behavior", None, "The ability to understand and apply animal behavior concepts."
    )
    animal_psychology = Skill(
        "Animal Psychology", None, "The ability to understand and apply animal psychology concepts."
    )
    animal_sociology = Skill(
        "Animal Sociology", None, "The ability to understand and apply animal sociology concepts."
    )
    animal_anatomy = Skill(
        "Animal Anatomy", None, "The ability to understand and apply animal anatomy concepts."
    )
    animal_physiology = Skill(
        "Animal Physiology", None, "The ability to understand and apply animal physiology concepts."
    )
    animal_genetics = Skill(
        "Animal Genetics", None, "The ability to understand and apply animal genetics concepts."
    )
    animal_reproduction = Skill(
        "Animal Reproduction", None, "The ability to understand and apply animal reproduction concepts."
    )
    animal_diseases = Skill(
        "Animal Diseases", None, "The ability to understand and apply animal diseases concepts."
    )
    animal_medicine = Skill(
        "Animal Medicine", None, "The ability to understand and apply animal medicine concepts."
    )
    animal_surgery = Skill(
        "Animal Surgery", None, "The ability to understand and apply animal surgery concepts."
    )
    animal_pharmacology = Skill(
        "Animal Pharmacology", None, "The ability to understand and apply animal pharmacology concepts."
    )
    animal_nursing = Skill(
        "Animal Nursing", None, "The ability to understand and apply animal nursing concepts."
    )
    animal_therapy = Skill(
        "Animal Therapy", None, "The ability to understand and apply animal therapy concepts."
    )


task_requirements: dict[Skills, set[Skill]] = defaultdict(set)


def add_skill_requirements(A, B):
    task_requirements[A].add(B)


def get_skill_requirements(A):
    return task_requirements[A]


def remove_skill_requirements(A, B):
    task_requirements[A].remove(B) if B in task_requirements[A] else None
