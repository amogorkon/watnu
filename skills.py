class Skill:
    _icon: str | None = ""
    _description_en: str = ""
    _description_de: str | None = None
    _description_es: str | None = None
    _primary_activity: int = None
    _secondary_activity: int = None
    _priority: float = 0

    @classmethod
    @property
    def icon(cls):
        return cls._icon

    @classmethod
    @property
    def description_en(cls):
        return cls._description_en

    @classmethod
    @property
    def description_de(cls):
        return cls._description_de

    @classmethod
    @property
    def description_es(cls):
        return cls._description_es

    @classmethod
    @property
    def primary_activity(cls):
        return cls._primary_activity

    @classmethod
    @property
    def secondary_activity(cls):
        return cls._secondary_activity

    @classmethod
    @property
    def priority(cls):
        return cls._priority

    @classmethod
    @property
    def name(cls):
        return None if cls.__name__ == "Skill" else cls.__name__

    @classmethod
    @property
    def parents(cls):
        return [cls.parents for cls in cls.__bases__] if cls.__bases__ != (Skill,) else cls.name


class Reading(Skill):
    pass


class Math(Reading):
    _icon = "maad maths af"
