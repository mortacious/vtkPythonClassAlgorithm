from collections import Sequence

def assert_list(input):
    if not isinstance(input, Sequence) or isinstance(input, str):
        input = [input]
    return input

def convert_elements(elem, type):
    if not isinstance(elem, Sequence) or isinstance(elem, str):
        return type(elem)
    else:
        return [type(l) for l in elem]

def get_type(elem):
    if not isinstance(elem, Sequence) or isinstance(elem, str):
        return type(elem)
    else:
        t = type(elem[0])
        for e in elem:
            if type(e) != t:
                raise TypeError("List elements have different types")

        return t

TYPE_PROPERTIES = {
    str : 'StringVectorProperty',
    bool : 'IntVectorProperty',
    int : 'IntVectorProperty',
    float : 'DoubleVectorProperty'
}


VISIBILITY = {'default', 'advanced', 'never'}

class PvProperty(object):
    def __init__(self,
                 initial_value,
                 name,
                 label=None,
                 initial_string = None,
                 data_type=None,
                 num_elements=None,
                 doc="",
                 domain=None,
                 visibility='default',
                 command='SetParameter',
                 animatable=True):
        self.value = initial_value
        self.name = name
        if data_type is None:
            self.type = get_type(self.value)
        else:
            self.type = data_type

        if self.type not in TYPE_PROPERTIES:
            raise AttributeError("type {0} not allowed".format(self.type))

        self.value = convert_elements(self.value, self.type)

        if label is None:
            label = self.name
        self.label = label

        if initial_string is None:
            initial_string = self.name

        self.initial_string = initial_string

        if num_elements is None:
            tmp = assert_list(self.value)
            num_elements = len(tmp)
        self.num_elements = num_elements
        self.doc = doc
        self.domain = domain

        if visibility not in VISIBILITY:
            raise AttributeError("invalid visibility")
        self.visibility = visibility
        self.command = command
        self.animatable = animatable

    def __call__(self, value=None):
        if value is None:
            return self.value
        else:
            value = convert_elements(value, self.type)
            if type(value) is str:
                length = 1
            else:
                try:
                    length = len(value)
                except TypeError:
                    length = 1

            if length != self.num_elements:
                raise ValueError("need {0} elements. Got {1}".format(self.num_elements, length))
            self.value = value

    # def __get__(self, instance, owner):
    #     print(instance, owner)
    #     return self.value
    #
    # def __set__(self, instance, value):
    #
    #

    def generate_xml(self):
        from lxml import etree
        default_values = ' '.join(str(self.type(v)) for v in assert_list(self.value))
        children = []
        if self.type is bool:
            default_values = default_values.replace('True', '1').replace('False', '0')
            children.append(etree.Element('BooleanDomain', name="bool"))

        if self.doc:
            doc = etree.Element('Documentation')
            doc.text = self.doc
            children.append(doc)

        if self.domain is not None:
            children.extend(self.domain)

        if self.animatable:
            animatable = '1'
        else:
            animatable = '0'

        elem = etree.Element(TYPE_PROPERTIES[self.type],
                            name=self.name,
                            label=self.label,
                            default_values=default_values,
                            number_of_elements=str(self.num_elements),
                            panel_visibility=self.visibility,
                            command=self.command,
                            animatable=animatable)

        if self.initial_string is not None:
            elem.attrib["initial_string"] = self.initial_string

        elem.extend(children)

        return elem


class PvFileProperty(PvProperty):
    def __init__(self, initial_value, name, label=None, initial_string=None, doc="", visibility='default', animatable=True):
        from lxml import etree
        domain_elem = etree.Element('FileListDomain', name="files")
        super(PvFileProperty, self).__init__(initial_value,
                                             name,
                                             label=label,
                                             initial_string=initial_string,
                                             data_type=str,
                                             num_elements=1,
                                             doc=doc,
                                             domain=domain_elem,
                                             visibility=visibility,
                                             animatable=animatable)

class PvSliderProperty(PvProperty):
    def __init__(self, initial_value, name, min, max, label=None, initial_string=None, doc="", visibility='default', animatable=True):
        from lxml import etree
        default_value = assert_list(initial_value)
        if len(default_value) > 1:
            raise AttributeError("Only one element allowed for SliderProperty")

        min_value = assert_list(min)
        if len(min_value) > 1:
            raise AttributeError("Only one element allowed for SliderProperty")

        max_value = assert_list(max)
        if len(max_value) > 1:
            raise AttributeError("Only one element allowed for SliderProperty")

        domain_name = 'DoubleRangeDomain'
        domain_elem = etree.Element(domain_name, name="range", min=str(type(min_value[0])), max=str(type(max_value[0])))

        super(PvSliderProperty, self).__init__(initial_value,
                                               name,
                                               label=label,
                                               initial_string=initial_string,
                                               data_type=float,
                                               num_elements=1,
                                               doc=doc,
                                               domain=domain_elem,
                                               visibility=visibility,
                                               animatable=animatable)



class EnumerationProperty(PvProperty):
    def __init__(self, initial_value, name, elements, label=None, initial_string=None, doc="", visibility='default', animatable=True):
        from lxml import etree
        default_value = assert_list(initial_value)
        if len(default_value) > 1:
            raise AttributeError("Only one element allowed for EnumerationProperty")

        if not isinstance(elements, list):
            raise AttributeError("A List is required for the elements parameter")

        if initial_value not in elements:
            raise AttributeError("initial_value must be in elements")

        domain_elem = etree.Element('EnumerationDomain', name="enum")
        for i,v in enumerate(elements):
            etree.SubElement(domain_elem, 'Entry', value=str(type(v)), text=str(i))

        super(EnumerationProperty, self).__init__(initial_value,
                                                  name,
                                                  label=label,
                                                  initial_string=initial_string,
                                                  data_type=int,
                                                  num_elements=1,
                                                  doc=doc,
                                                  domain=domain_elem,
                                                  visibility=visibility,
                                                  animatable=animatable)


class PvPythonPathProperty(PvProperty):
    def __init__(self, *paths):
        joined_path = ';'.join(paths)
        super(PvPythonPathProperty, self).__init__(joined_path,
                                                   'PythonPath',
                                                   label='PythonPath',
                                                   initial_string=None,
                                                   data_type=str,
                                                   num_elements=1,
                                                   doc="A semi-colon (;) separated list of directories to add to the python library search path.",
                                                   visibility='advanced',
                                                   command='SetPythonPath')

    def generate_xml(self):
        from lxml import etree

        self.value = '"' + self.value + '"'
        default_values = ' '.join(str(self.type(v)) for v in assert_list(self.value))
        children = []
        if self.type is bool:
            default_values = default_values.replace('True', '1').replace('False', '0')
            children.append(etree.Element('BooleanDomain', name="bool"))

        if self.doc:
            doc = etree.Element('Documentation')
            doc.text = self.doc
            children.append(doc)

        if self.domain is not None:
            children.extend(self.domain)

        if self.animatable:
            animatable = '1'
        else:
            animatable = '0'

        elem = etree.Element(TYPE_PROPERTIES[self.type],
                             name=self.name,
                             label=self.label,
                             default_values=default_values,
                             number_of_elements=str(self.num_elements),
                             panel_visibility=self.visibility,
                             command=self.command,
                             animatable=animatable)

        if self.initial_string is not None:
            elem.attrib["initial_string"] = self.initial_string

        elem.extend(children)

        return elem

    def append(self, *paths):
        self.value += ';' + ';'.join(paths)


if __name__ == "__main__":
    class TestClass(object):
        p = PvProperty([0, 1, 2, 3], "p")
        path = PvPythonPathProperty('/foo/bar', '/baz/')


    t = TestClass()

    print(t.p())

    t.p([4,5,6, 7])

    print(t.p())

    print(t.path())

    t.path.append('/hello/world')

    print(t.path())



    # testProperty = Property("TestProperty", "Test Property", str, 2, [10, 15], docstring="Hello World")
    # elem = testProperty.generate_xml()
    # print(etree.tostring(elem, pretty_print=True))
    #
    #
    # testFileProperty = FileProperty("TestFileProperty", "Test File Property", docstring="Hello File")
    # elem = testFileProperty.generate_xml()
    # print(etree.tostring(elem, pretty_print=True))
    #
    # testSliderProperty = SliderProperty("TestSliderProperty", "Test Slider Property", float, 0.1, 0.0, 2.0)
    # elem = testSliderProperty.generate_xml()
    # print(etree.tostring(elem, pretty_print=True))
    #
    # testEnumerationProperty = EnumerationProperty("TestEnumerationProperty", "Test Enumeration Property", str, 1, {"One": 1, "Two": 2}, panel_visibility='advanced')
    # elem = testEnumerationProperty.generate_xml()
    # print(etree.tostring(elem, pretty_print=True))
    #
    # testPythonPathProperty = PythonPathProperty('foo', 'bar', 'baz')
    # elem = testPythonPathProperty.generate_xml()
    # print(etree.tostring(elem, pretty_print=True))