mongo=(mongo --host 127.0.0.1 --port $MONGO_PORT --quiet)
mongo+=(
    --username="$MONGO_INITDB_ROOT_USERNAME"
    --password="$MONGO_INITDB_ROOT_PASSWORD"
    --authenticationDatabase="$rootAuthDatabase"
)

INSERT_FILES=/*-insert.js
for f in $INSERT_FILES; do "${mongo[@]}" "$MONGO_INITDB_DATABASE" $f; done
