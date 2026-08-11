"""
Библиотека для создания ИИ-систем уровня Bug Bounty в области кибербезопасности (CAI).
"""


def is_pentestperf_available():
    """
    Проверяет, доступен ли caibench (ранее pentestperf)
    """
    try:
        from cai.caibench.ctf import CTF  # pylint: disable=import-error,import-outside-toplevel,unused-import  # noqa: E501,F401
    except ImportError:
        return False
    return True


def is_caiextensions_report_available():
    """
    Проверяет, доступно ли расширение caiextensions report
    """
    try:
        from caiextensions.report.common import get_base_instructions  # pylint: disable=import-error,import-outside-toplevel,unused-import  # noqa: E501,F401
    except ImportError:
        return False
    return True


def is_caiextensions_memory_available():
    """
    Проверяет, доступно ли расширение caiextensions memory
    """
    try:
        from caiextensions.memory import is_memory_installed  # pylint: disable=import-error,import-outside-toplevel,unused-import  # noqa: E501,F401
    except ImportError:
        return False
    return True
