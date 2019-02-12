@SETLOCAL

@REM Set the PYTHON path variable to your python command, like C:\Python33\python.exe
@IF "%PYTHON%" == "" echo Warning: PYTHON environment path not set.

@IF "%DLLPATH_X86%" == "" SET DLLPATH_X86=%CD%\..\dlls\32bit
@IF "%DLLPATH_X64%" == "" SET DLLPATH_X64=%CD%\..\dlls\64bit
@IF "%PYTHONPATH%" == "" SET PYTHONPATH=%CHDIR%
@IF "%PYTHON27_X86%" == "" SET PYTHON27_X86=c:\Python27-x86\python.exe
@IF "%PYTHON27_X64%" == "" SET PYTHON27_X64=c:\Python27-x64\python.exe
@IF "%PYTHON35_X86%" == "" SET PYTHON35_X86=c:\Python35-x86\python.exe
@IF "%PYTHON35_X64%" == "" SET PYTHON35_X64=c:\Python35-x64\python.exe
@IF "%PYTHON36_X86%" == "" SET PYTHON36_X86=c:\Python36-x86\python.exe
@IF "%PYTHON36_X64%" == "" SET PYTHON36_X64=c:\Python36-x64\python.exe
@IF "%PYTHON%" == "" SET PYTHON=%PYTHON27_X64%
@IF "%PYPY2%" == "" SET PYPY2=c:\pypy2-v5.7.1\pypy.exe
@REM IF "%PYPY3%" == "" SET PYPY3=c:\pypy3-v2.4\pypy.exe

@SET INTERP_X64=%PYTHON27_X64%;%PYTHON35_X64%;%PYTHON36_X64%
@SET INTERP_X86=%PYTHON27_X86%;%PYTHON35_X86%;%PYTHON36_X86%;%PYPY2%
@SET INTERPRETERS=%INTERP_X86%;%INTERP_X64%

@IF "%~1" == "" GOTO :all
@GOTO :%~1

:all
@CALL :clean
@CALL :build
@GOTO :eof

:dist
@ECHO Creating dist...
@CALL :clean
@CALL :docs
@%PYTHON% setup.py sdist --format gztar
@%PYTHON% setup.py sdist --format zip
@GOTO :eof

:bdist
@CALL :clean
@CALL :docs
@ECHO Creating bdist...
@FOR %%A in (%INTERPRETERS%) do %%A setup.py bdist --format=msi
@GOTO :eof

:build
@ECHO Running build
@%PYTHON% setup.py build
@ECHO Build finished, invoke 'make install' to install.
@GOTO :eof

:install
@ECHO Installing...
@%PYTHON% setup.py install
@GOTO :eof

:clean
@RMDIR /S /Q build
@RMDIR /S /Q dist
@FOR /d /r . %%d in (__pycache__) do @IF EXIST "%%d" RMDIR /S /Q "%%d"
@DEL /S /Q MANIFEST
@DEL /S /Q *.pyc

@GOTO :eof

:docs
@IF "%SPHINXBUILD%" == "" SET SPHINXBUILD=C:\Python27-x64\Scripts\sphinx-build.exe
@ECHO Creating docs package
@RMDIR /S /Q doc\html
@CD doc
@CALL make html
@MOVE /Y _build\html html
@RMDIR /S /Q _build
@CALL make clean
@CD ..
@GOTO :eof

:release
@CALL :dist
@GOTO :eof

:testall
@FOR /F "tokens=1 delims=" %%A in ('CHDIR') do @SET PYTHONPATH=%%A
@SET PYSDL2_DLL_PATH=%DLLPATH_X86%
@FOR %%A in (%INTERP_X86%) do @%%A -B -m unittest discover sdl2.test -p *test.py -v
@SET PYSDL2_DLL_PATH=%DLLPATH_X64%
@FOR %%A in (%INTERP_X64%) do @%%A -B -m unittest discover sdl2.test -p *test.py -v
@GOTO :eof

@REM Do not run these in production environments. They are for testing purposes
@REM only!

:buildall
@FOR %%A in (%INTERPRETERS%) do @CALL :clean & @%%A setup.py build
@CALL :clean
@GOTO :eof

:installall
@FOR %%A in (%INTERPRETERS%) do @CALL :clean & @%%A setup.py install
@CALL :clean
@GOTO :eof

:purge_installs
@echo Deleting data...
@RMDIR /S /Q C:\Python27-x86\Lib\site-packages\sdl2
@RMDIR /S /Q C:\Python27-x64\Lib\site-packages\sdl2
@RMDIR /S /Q C:\Python35-x86\Lib\site-packages\sdl2
@RMDIR /S /Q C:\Python35-x64\Lib\site-packages\sdl2
@RMDIR /S /Q C:\Python36-x86\Lib\site-packages\sdl2
@RMDIR /S /Q C:\Python36-x64\Lib\site-packages\sdl2
@RMDIR /S /Q C:\pypy2-v5.7.1\site-packages\sdl2
@REM RMDIR /S /Q C:\pypy3-2.4\site-packages\sdl2
@echo done
@GOTO :eof

@ENDLOCAL
