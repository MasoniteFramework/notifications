from abc import abstractmethod

class StaticallyCallable(type):
    def __getattr__(self, attribute, *args, **kwargs):
        from wsgi import container
        instance = container.make(self.__service__)
        return getattr(instance, attribute)


class MockableService(object, metaclass=StaticallyCallable):

    __service__ = ""

    @abstractmethod
    def get_mock_class():
        raise NotImplementedError(
            "get_mock_class() method must be implemented for a mockable service."
        )

    @classmethod
    def fake(cls):
        from wsgi import container
        mock_instance = cls.get_mock_class()(container)
        container.bind(cls.__service__, mock_instance)
        return mock_instance

    @classmethod
    def restore(cls):
        from wsgi import container
        original_instance = cls(container)
        container.bind(cls.__service__, original_instance)
        return original_instance
