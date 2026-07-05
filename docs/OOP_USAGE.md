# OOP Usage in LMPTS

## Inheritance

```python
class Identifiable(ABC):
    @abstractmethod
    def id(self) -> str: ...

class TimestampedEntity(Identifiable, ABC):
    # created_at, updated_at tracking

class Course(TimestampedEntity):
    # Concrete implementation
```

## Encapsulation

```python
class Course:
    _prerequisites: Set[str]  # Private

    @property
    def prerequisites(self) -> Set[str]:
        return self._prerequisites.copy()  # Defensive copy
```

## Polymorphism

```python
class ShortestPathStrategy(PathFindingStrategy): ...
class DifficultyProgressiveStrategy(PathFindingStrategy): ...

finder.set_strategy(ShortestPathStrategy())  # or any strategy
```

## Abstraction

Repository ABC hides persistence details from services.

## Composition

`ServiceContainer` composes repositories, graph, and services.

## Dependency Injection

```python
container = ServiceContainer(db_path)
container.course_service.create_course(...)
```
