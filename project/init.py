import time
import argparse
from helpers.connection import conn

if __name__ == "__main__":
    try:
        cur = conn.cursor()

        # create orders_id_seq
        sql = "CREATE SEQUENCE public.orders_id_seq INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1; ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;"
        cur.execute(sql)
        conn.commit()

        # create orders table
        sql="CREATE TABLE public.orders (id integer NOT NULL DEFAULT nextval('orders_id_seq'::regclass),cid integer NOT NULL,sid integer NOT NULL,mid integer NOT NULL,menu_name character varying COLLATE pg_catalog."+"default"+" NOT NULL,menu_count integer NOT NULL,did integer,order_time timestamp without time zone,delivered_time timestamp without time zone,status integer NOT NULL,payment jsonb,cphone character varying COLLATE pg_catalog."+"default"+", CONSTRAINT orders_pkey PRIMARY KEY (id))TABLESPACE pg_default;ALTER TABLE public.orders OWNER to postgres;"
        cur.execute(sql)
        conn.commit()
        
        # add column addresses in customer
        sql="ALTER TABLE customer ADD COLUMN addresses text[] COLLATE pg_catalog."+"default" 
        cur.execute(sql)
        conn.commit()

        # add column cart in customer
        sql = "ALTER TABLE customer ADD COLUMN cart jsonb;"
        cur.execute(sql)
        conn.commit()
    except Exception as err:
        print(err)
        # print(args)
    pass

