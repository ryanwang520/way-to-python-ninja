#include <Python.h>


static PyObject *SpamError;


static PyObject *spam_system(PyObject *self, PyObject *args) {
  const char *command;
  int sts;

  if (!PyArg_ParseTuple(args, "s", &command))
    return NULL;
   sts = system(command);
   if (sts < 0) {
    PyErr_SetString(SpamError, "System command failed");
    return NULL;
   }
   return PyLong_FromLong(sts);
};

static int factorial(int n) {
  if (n == 0) {
      return 1;
  }
  return factorial(n-1) * n;
};


static PyObject *spam_factorial(PyObject *self, PyObject *args) {

  int n;
  if (!PyArg_ParseTuple(args, "i", &n))
    return NULL;
   if (n < 0) {
      PyErr_SetString(SpamError, "factorial should act on a positive number");
      return NULL;
   }
   return PyLong_FromLong(factorial(n));
};


static PyMethodDef SpamMethods[] = {
    {"system", spam_system, METH_VARARGS, "Execute a shell command."},
    {"factorial", spam_factorial, METH_VARARGS, "factorial for a number"},
    {NULL, NULL, 0, NULL}
};


static struct PyModuleDef spammodule = {
    PyModuleDef_HEAD_INIT,
    "spam",
    "spam document",
    -1,
    SpamMethods
};

PyMODINIT_FUNC PyInit_spam(void) {
    PyObject *m;

    m = PyModule_Create(&spammodule);
    if (m == NULL)
        return NULL;

    SpamError = PyErr_NewException("spam.error", NULL, NULL);
    Py_INCREF(SpamError);
    PyModule_AddObject(m, "error", SpamError);
    return m;
};
