using TOML

function load_config()
    return TOML.parsefile("config/config.toml")
end
