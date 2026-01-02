using System.Data;
using System.Text.Json.Nodes;
using Newtonsoft.Json;

class Program
{
    public static string DataTableToJsonArray(DataTable dataTable)
    {
        return JsonConvert.SerializeObject(dataTable);
    }

    public static string DataTableToJsonWithKeys(DataTable dataTable)
    {
        var dict = new Dictionary<string, Dictionary<string, object>>();

        foreach (DataRow row in dataTable.Rows)
        {
            var key = row["cardID"]?.ToString();

            if (string.IsNullOrEmpty(key))
                continue;

            var obj = new Dictionary<string, object>();

            foreach (DataColumn col in dataTable.Columns)
            {
                var value = row[col];
                obj[col.ColumnName] = value == DBNull.Value ? null : value;
            }

            dict[key] = obj;
        }

        return JsonConvert.SerializeObject(dict, Formatting.Indented);
    }

    static void GetTCGDataBaseAsJson(Boolean jsonWithKeys)
    {
        var inputDir = Path.Combine(Environment.CurrentDirectory, "config-cache");
        var inputDirJson = Path.Combine(Environment.CurrentDirectory, "config-cache-json");

        if (!Directory.Exists(inputDir))
        {
            Console.WriteLine($"Folder not found: {inputDir}");
            return;
        }

        var files = Directory.GetFiles(inputDir, "card-database-*_0_en_0.0.json");

        if (files.Length == 0)
        {
            Console.WriteLine("No matching files found.");
            return;
        }

        Directory.CreateDirectory(inputDirJson);

        foreach (var file in files)
        {
            Console.WriteLine($"Processing {Path.GetFileName(file)}");

            var jsonText = File.ReadAllText(file);
            var root = JsonNode.Parse(jsonText);

            var base64 = root?["keys"]?["table"]?["contentBinary"]?.GetValue<string>();

            if (string.IsNullOrWhiteSpace(base64))
            {
                Console.WriteLine("  ❌ contentBinary not found");
                continue;
            }

            var bytes = Convert.FromBase64String(base64);
            //Console.WriteLine(bytes);

            var deserializedTable = CardDatabase.DataAccess.DataTableCustomFormatter.Deserialize(bytes);

            var output = jsonWithKeys ? DataTableToJsonWithKeys(deserializedTable) : DataTableToJsonArray(deserializedTable);

            var outputPath = Path.Combine(
                inputDirJson,
                Path.GetFileNameWithoutExtension(file) + "_contents.json"
            );

            File.WriteAllText(outputPath, output);
        }

        Console.WriteLine("Done.");
    }

    static void Main()
    {
        GetTCGDataBaseAsJson(jsonWithKeys: true);
    }

}
