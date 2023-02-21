
CREATE TABLE campains (
    msg_body TEXT
);

CREATE TABLE sent_msg (
    twilio_sid TEXT, 
    phone_number TEXT,
    first_name TEXT,
    last_name TEXT,
    campain_id TEXT,
    ts TIMESTAMP 
);


CREATE TABLE pnms (
     semester TEXT,
     first_name TEXT,
     last_name TEXT,
     campains TEXT
);