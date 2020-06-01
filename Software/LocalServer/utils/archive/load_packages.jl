metadata_packages = [
    "DataStreams",
    "JuliaDB",
    "IterableTables",
    "DataStructures",
    "HTTP",
    "JSON",
    "MySQL",
    "Formatting"]

Pkg.init()
Pkg.update()

for package=metadata_packages
    Pkg.add(package)
end

Pkg.resolve()

for packs in metadata_packages
    eval(parse("using $packs"))
end

Pkg.clone("https://github.com/wildart/TOML.jl.git")
using TOML
