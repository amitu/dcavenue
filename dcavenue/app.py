from importd import d


d(
    DEBUG=True,
    INSTALLED_APPS=["dcavenue"],
    TEST_RUNNER='django_nose.NoseTestSuiteRunner',
)

if __name__ == "__main__":
    d.main()