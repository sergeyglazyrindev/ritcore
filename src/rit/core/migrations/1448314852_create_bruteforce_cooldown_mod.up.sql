/**Up migration
create bruteforce cooldown model**/
create table bruteforce_cooldown(
    id serial PRIMARY KEY,
    resource varchar(100) not null default '',
    client varchar(45) not null default '',
    threshold integer not null default 0,
    period bigint not null default 0,
    cooldown bigint not null default 0,
    started timestamp not null default CURRENT_TIMESTAMP,
    expires_at timestamp not null,
    CONSTRAINT resource_client_constraint UNIQUE (resource, client)
)
