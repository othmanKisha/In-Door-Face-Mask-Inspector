function getEnvValue(envVar, defVal) {
    var ret= run("sh", "-c", `printenv ${envVar} >/tmp/${envVar}.txt`);
    if (ret != 0) return defVal;
    return cat(`/tmp/${envVar}.txt`)
 }

db.settings.drop();

db.settings.insert({
    id: 0,
    confidence: parseFloat(getEnvValue('INIT_CONFIDENCE', 0.5))
});
