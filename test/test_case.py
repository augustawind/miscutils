from miscutils import case as c


class TestCaseConversions:

    data = {
        c.PascalCase: ('Foo', 'FooBar', 'XFoo', 'FooX', 'FooXBar', 'Foo3',
                       'Foo3Bar'),
        c.CamelCase: ('foo', 'fooBar', 'xFoo', 'fooX', 'fooXBar', 'foo3',
                      'foo3Bar'),
        c.SnakeCase: ('foo', 'foo_bar', 'x_foo', 'foo_x', 'foo_x_bar', 'foo3',
                      'foo3_bar'),
        c.KebabCase: ('foo', 'foo-bar', 'x-foo', 'foo-x', 'foo-x-bar', 'foo3',
                      'foo3-bar'),
    }

    formats = ('{}', '_{}', '__{}')

    def run_test(self, start_case, end_case):
        for start, end in zip(self.data[start_case], self.data[end_case]):
            for fmt in self.formats:
                start, end = fmt.format(start), fmt.format(end)
                assert str(start_case(start).to_case(end_case)) == end

    def test_camel_to_camel(self):
        self.run_test(c.CamelCase, c.CamelCase)

    def test_camel_to_snake(self):
        self.run_test(c.CamelCase, c.SnakeCase)

    def test_camel_to_kebab(self):
        self.run_test(c.CamelCase, c.KebabCase)

    def test_snake_to_snake(self):
        self.run_test(c.SnakeCase, c.SnakeCase)

    def test_snake_to_camel(self):
        self.run_test(c.SnakeCase, c.CamelCase)

    def test_snake_to_kebab(self):
        self.run_test(c.SnakeCase, c.KebabCase)

    def test_kebab_to_kebab(self):
        self.run_test(c.KebabCase, c.KebabCase)

    def test_kebab_to_camel(self):
        self.run_test(c.KebabCase, c.CamelCase)

    def test_kebab_to_snake(self):
        self.run_test(c.KebabCase, c.SnakeCase)
