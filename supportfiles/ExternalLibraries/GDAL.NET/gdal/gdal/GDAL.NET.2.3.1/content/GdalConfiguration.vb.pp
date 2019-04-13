'******************************************************************************
'*
'* Name:     GdalConfiguration.cs.pp
'* Project:  GDAL CSharp Interface
'* Purpose:  A static configuration utility class to enable GDAL/OGR.
'* Author:   Felix Obermaier
'*
'******************************************************************************
'* Copyright (c) 2012, Felix Obermaier
'*
'* Permission is hereby granted, free of charge, to any person obtaining a
'* copy of this software and associated documentation files (the "Software"),
'* to deal in the Software without restriction, including without limitation
'* the rights to use, copy, modify, merge, publish, distribute, sublicense,
'* and/or sell copies of the Software, and to permit persons to whom the
'* Software is furnished to do so, subject to the following conditions:
'*
'* The above copyright notice and this permission notice shall be included
'* in all copies or substantial portions of the Software.
'*
'* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
'* OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
'* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
'* THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
'* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
'* FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
'* DEALINGS IN THE SOFTWARE.
'*****************************************************************************/

Option Infer On

Imports System
Imports System.IO
Imports System.Reflection
Imports Gdal = OSGeo.GDAL.Gdal
Imports Ogr = OSGeo.OGR.Ogr

Namespace $rootnamespace$
    ''' <summary>
    ''' Configuration class for GDAL/OGR
    ''' </summary>
    Partial Public NotInheritable Class GdalConfiguration
        Private Sub New()
        End Sub
        Private Shared _configuredOgr As Boolean
        Private Shared _configuredGdal As Boolean

        Private Shared Function VolatileRead(Of T)(ByRef Address As T) As T
            VolatileRead = Address
            Threading.Thread.MemoryBarrier()
        End Function

        Private Shared Sub VolatileWrite(Of T)(ByRef Address As T, ByVal Value As T)
            Threading.Thread.MemoryBarrier()
            Address = Value
        End Sub

        ''' <summary>
        ''' Function to determine which platform we're on
        ''' </summary>
        Private Shared Function GetPlatform() As String
            Return If(IntPtr.Size = 4, "x86", "x64")
        End Function


        ''' <summary>
        ''' Construction of Gdal/Ogr
        ''' </summary>
        Shared Sub New()
            Dim executingAssemblyFile = New Uri(Assembly.GetExecutingAssembly().GetName().CodeBase).LocalPath
            Dim executingDirectory = Path.GetDirectoryName(executingAssemblyFile)

            If String.IsNullOrEmpty(executingDirectory) Then
                Throw New InvalidOperationException("cannot get executing directory")
            End If


            Dim gdalPath = Path.Combine(executingDirectory, "gdal")
            Dim nativePath = Path.Combine(gdalPath, GetPlatform())

            ' Prepend native path to environment path, to ensure the
            ' right libs are being used.
            Dim path__1 = Environment.GetEnvironmentVariable("PATH")
            path__1 = nativePath & ";" & Path.Combine(nativePath, "plugins") & ";" & path__1
            Environment.SetEnvironmentVariable("PATH", path__1)

            ' Set the additional GDAL environment variables.
            Dim gdalData = Path.Combine(gdalPath, "data")
            Environment.SetEnvironmentVariable("GDAL_DATA", gdalData)
            Gdal.SetConfigOption("GDAL_DATA", gdalData)

            Dim driverPath = Path.Combine(nativePath, "plugins")
            Environment.SetEnvironmentVariable("GDAL_DRIVER_PATH", driverPath)
            Gdal.SetConfigOption("GDAL_DRIVER_PATH", driverPath)

            Environment.SetEnvironmentVariable("GEOTIFF_CSV", gdalData)
            Gdal.SetConfigOption("GEOTIFF_CSV", gdalData)

            Dim projSharePath = Path.Combine(gdalPath, "share")
            Environment.SetEnvironmentVariable("PROJ_LIB", projSharePath)
            Gdal.SetConfigOption("PROJ_LIB", projSharePath)
        End Sub

        ''' <summary>
        ''' Method to ensure the static constructor is being called.
        ''' </summary>
        ''' <remarks>Be sure to call this function before using Gdal/Ogr/Osr</remarks>
        Public Shared Sub ConfigureOgr()

            Call VolatileRead(_configuredOgr)
            If _configuredOgr Then
                Return
			End If

            ' Register drivers
            Ogr.RegisterAll()
            Call VolatileWrite(_configuredOgr, True)

            PrintDriversOgr()
        End Sub

        ''' <summary>
        ''' Method to ensure the static constructor is being called.
        ''' </summary>
        ''' <remarks>Be sure to call this function before using Gdal/Ogr/Osr</remarks>
        Public Shared Sub ConfigureGdal()
            Call VolatileRead(_configuredGdal)
            If _configuredGdal Then
                Return
            End If

            ' Register drivers
            Gdal.AllRegister()
            Call VolatileWrite(_configuredGdal, True)

            PrintDriversGdal()
        End Sub

        Private Shared Sub PrintDriversOgr()
#If DEBUG Then
            Dim num = Ogr.GetDriverCount()
            For i As var = 0 To num - 1
                Dim driver = Ogr.GetDriver(i)
                Console.WriteLine(String.Format("OGR {0}: {1}", i, driver.Name))
            Next
#End If
        End Sub

        Private Shared Sub PrintDriversGdal()
#If DEBUG Then
            Dim num = Gdal.GetDriverCount()
            For i As var = 0 To num - 1
                Dim driver = Gdal.GetDriver(i)
                Console.WriteLine(String.Format("GDAL {0}: {1}-{2}", i, driver.ShortName, driver.LongName))
            Next
#End If
        End Sub
    End Class
End Namespace