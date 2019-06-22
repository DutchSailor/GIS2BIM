using System;
using System.Collections.Generic;
using BitMiracle.LibTiff.Classic;

/// <summary>
/// </summary>
public static class Helpers
{
    /// <summary>
    /// Reads a GEOTiff file and returns coordinate and elevation data
    /// </summary>
    /// <param name="filePath">Path of GEOTiff file</param>
    /// <returns>returns a list of objects with the following fields: latitude, longitude and elevation</returns>
    public static List<Dictionary<string, double>> GEOTiffReader(string filePath)
    {
        using (var tiff = Tiff.Open(filePath, "r"))
        {
            var height = tiff.GetField(TiffTag.IMAGELENGTH)[0].ToInt();
            var modelPixelScaleTag = tiff.GetField(TiffTag.GEOTIFF_MODELPIXELSCALETAG);
            var modelTiePointTag = tiff.GetField(TiffTag.GEOTIFF_MODELTIEPOINTTAG);

            var modelPixelScale = modelPixelScaleTag[1].GetBytes();
            var pixelSizeX = BitConverter.ToDouble(modelPixelScale, 0);
            var pixelSizeY = BitConverter.ToDouble(modelPixelScale, 8) * -1;

            var modelTransformation = modelTiePointTag[1].GetBytes();
            var originLon = BitConverter.ToDouble(modelTransformation, 24);
            var originLat = BitConverter.ToDouble(modelTransformation, 32);

            var startLat = originLat + pixelSizeY / 2.0;
            var startLon = originLon + pixelSizeX / 2.0;

            var scanLineSize = tiff.ScanlineSize();
            var scanLine = new byte[scanLineSize];

            var currentLat = startLat;
            var currentLon = startLon;

            const int numberOfElevationBytes = 4;

            var result = new List<Dictionary<string, double>>();
            for (var i = 0; i < height; i += 1)
            {
                tiff.ReadScanline(scanLine, i);
                var latitude = currentLat + pixelSizeY * i;
                for (var j = 0; j < scanLine.Length; j += numberOfElevationBytes)
                {
                    var longitude = currentLon + pixelSizeX * j / numberOfElevationBytes;
                    var elevation = BitConverter.ToSingle(scanLine, j);
                    result.Add(new Dictionary<string, double>
                    {
                        { "latitude", latitude },
                        { "longitude", longitude },
                        { "elevation", elevation }
                    });
                }
            }
            return result;
        }
    }
}
