@echo off
setlocal

IF [%1] == [-h] GOTO SHOW_HELP
IF [%1] == [--help] GOTO SHOW_HELP

pushd "%~dp0\content"
if errorlevel 1 goto PUSHD_ERROR

FOR /D /R . %%d IN (__pycache__) DO @IF EXIST "%%d" rd /s /q "%%d"
if errorlevel 1 goto DELETE_PYCACHE_ERROR

FOR /D /R . %%d IN (.ipynb_checkpoints) DO @IF EXIST "%%d" rd /s /q "%%d"
if errorlevel 1 goto DELETE_IPYNB_CHECKPOINTS_ERROR

del /s /q .*-*.ipynb >nul 2>&1
if errorlevel 1 goto DELETE_TEMP_IPYNB_ERROR

popd
exit /b 0

:SHOW_HELP
echo Cleanup unnecessary files into content directory
echo Utility deletes __pycache__, .ipynb_checkpoints directories
echo and .*-\d.pynb temporary files.
goto EXIT_ERROR

:DELETE_PYCACHE_ERROR
echo Cannot delete __pycache__ directories
goto EXIT_ERROR

:DELETE_IPYNB_CHECKPOINTS_ERROR
echo Cannot delete .ipynb_checkpoints directories
goto EXIT_ERROR

:DELETE_TEMP_IPYNB_ERROR
echo Cannot delete .*-*.ipynb temporery files
goto EXIT_ERROR

:PUSHD_ERROR
:EXIT_ERROR
popd
exit /b 1

