// wrapper.c

#include <Python.h>
#include "libexample.h" // Include the generated header from go build -buildmode=c-shared

static PyObject* py_add(PyObject* self, PyObject* args) {
    int a, b;
    if (!PyArg_ParseTuple(args, "ii", &a, &b)) {
        return NULL;
    }
    int result = Add(a, b);
    return Py_BuildValue("i", result);
}

static PyMethodDef ExampleMethods[] = {
    {"add", py_add, METH_VARARGS, "Add two integers"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef examplemodule = {
    PyModuleDef_HEAD_INIT,
    "example",
    NULL,
    -1,
    ExampleMethods
};

PyMODINIT_FUNC PyInit_example(void) {
    return PyModule_Create(&examplemodule);
}