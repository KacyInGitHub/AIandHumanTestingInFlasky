import coverage
import unittest

cov = coverage.Coverage(branch=True, include='app/*')
cov.start()

# 运行测试
unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('../tests/manual'))

cov.stop()
cov.save()

cov.report()
cov.html_report(directory='coverage_html')
