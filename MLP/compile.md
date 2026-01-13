# To compile, open msvc_x64.bat and type this in:

cd /d C:\Users\Gustavo6\Desktop\Gustavo\Programming\Projects\Unfinished\MLP
cl /nologo /LD /MD neurallib.c /I "C:\Users\Gustavo6\AppData\Local\Programs\Python\Python313\include" /link /OUT:neurallib.pyd /LIBPATH:"C:\Users\Gustavo6\AppData\Local\Programs\Python\Python313\libs" /LIBPATH:"C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\MSVC\14.38.33130\lib\x64" python313.lib
