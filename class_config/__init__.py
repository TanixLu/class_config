class ClassConfigMeta(type):
    def __new__(cls, name, bases, attrs, **kwargs):
        # 将kwargs加入attrs
        attrs.update(kwargs)

        # 遍历attrs，查找inner class并确保它们也继承自ClassConfigBase
        # 这样在使用ClassConfigBase的时候，inner class就不用显式地继承自ClassConfigBase了
        inner_class_names = set()
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith('_'):
                if isinstance(attr_value, type):
                    # 创建一个继承自ClassConfigBase和原始内部类的新类
                    inner_class_attrs = {k: v for k, v in vars(attr_value).items()}
                    new_inner_class = type(attr_name, (ClassConfigBase, attr_value), inner_class_attrs)
                    # 将原始内部类替换为新类
                    attrs[attr_name] = new_inner_class
                    # 记录内部类的名字，内部类的名字不能重复
                    inner_class_name = attr_value.name if hasattr(attr_value, 'name') else attr_name
                    if inner_class_name in inner_class_names:
                        raise ValueError(f'Inner class name "{inner_class_name}" is duplicated')
                    inner_class_names.add(inner_class_name)

        # 如果attrs中没有name，那么设置name为类名
        if 'name' not in attrs:
            attrs['name'] = name

        return super().__new__(cls, name, bases, attrs)

    def __getattr__(cls, item):
        return ClassConfigBase

    def __bool__(cls):
        return False

    def __eq__(cls, other):
        return False

    def __ne__(cls, other):
        return False


class ClassConfigBase(metaclass=ClassConfigMeta):
    """
    class Config(ClassConfigBase):
        class ParallelNum:
            name = '并行数量'

            value = 2

        class SubConfig:
            name = '子配置'

            class Speed:
                name = '速度'

                value = 3

            class Complex:  # 默认name为类名
                value = {'4': ['5', {'6': 7}]}

    assert Config.to_dict() == {'Config': {'并行数量': 2, '子配置': {'速度': 3, 'Complex': {'4': ['5', {'6': 7}]}}}}

    Attributes:
        name: 默认为类名。
        value: 总是存在，但是当有inner config时，优先使用inner config。
    """

    name = None
    value = None

    @classmethod
    def inner_configs(cls):
        """
        返回所有内部继承自ClassConfigBase的类，由于ClassConfigMeta会自动处理，
        因此这些类不一定显式继承自ClassConfigBase。
        """
        for entry in dir(cls):
            if not entry.startswith('_'):
                inner_class = getattr(cls, entry)
                # isinstance(inner_class, type)判断是否是类，等价于inspect.isclass(inner_class)
                if isinstance(inner_class, type) and issubclass(inner_class, ClassConfigBase):
                    yield inner_class

    @classmethod
    def is_leaf(cls):
        """ 没有inner config的是叶子配置 """
        return all(False for _ in cls.inner_configs())

    @classmethod
    def to_dict(cls):
        """ 将配置转换为dict """
        # 如果是叶子节点，直接返回value
        if cls.is_leaf():
            return {cls.name: cls.value}

        # 否则，递归调用to_dict方法
        dict_value = {}
        for inner_config in cls.inner_configs():
            dict_value.update(inner_config.to_dict())

        return {cls.name: dict_value}

    @classmethod
    def from_dict(cls, j):
        """ 将dict转换为配置 """
        if cls.name in j:
            j = j[cls.name]
            if cls.is_leaf():
                # 如果是叶子节点，递归终止，直接设置值
                cls.value = j
            elif isinstance(j, dict):
                # 对于非叶子节点，遍历inner config，进行递归调用
                for inner_config in cls.inner_configs():
                    if inner_config.name in j:
                        inner_config.from_dict(j)
