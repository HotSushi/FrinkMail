#!/usr/bin/env python

import sys
import psycopg2
import datetime


def parse_email(data):
    try:
        conn = psycopg2.connect(
            "dbname='hackathon_frink_dev' user='housing' host='amandeeps.housing.com' password='housing'")
    except:
        print "unable to connect to the database"
    cur = conn.cursor()

    # with open(file_name, "r") as myfile:
    #     data = myfile.read().replace('\n', '').replace('\r', '')
    data = data.replace('\n', '').replace('\r', '')

    if 'freecharge' in data:
        company = 'FreeCharge'
        try:
            s1 = data.index('Return-Path: <')
            s2 = data.index('.com', s1)
            email_id = data[s1 + 14:s2 + 4]
            print email_id
            cur.execute("select id from users where email='{email_id}'".format(
                email_id=email_id))
            rows = cur.fetchall()
            if len(rows) == 0:
                raise Exception("email-id not registered")
            user_id = rows[0][0]
            print user_id
            curr_indx = data.index('Insta coupon')
            while 1:
                t1 = data.index('[image:', curr_indx)
                t1a = data.index(']', t1)
                t2 = data.index('*', t1a)
                cpn = data[t1a + 2:t2 - 1]
                print cpn
                t3 = data.index('Expire on:', t2)
                exp = data[t3 + 13: t3 + 23]
                exp = datetime.datetime.strptime(
                    exp, '%Y-%m-%d').strftime('%d/%m/%y')
                print exp
                t4 = data.index('Terms & Conditions', t3)
                t5 = data.index('Lots of love', t4)
                t6 = data.find('[image:', t4)
                if not t6 > 0:
                    t6 = t5
                tnc = data[t4 + 21:t6 - 1]
                print tnc
                query = "insert into offer_infos(user_id,title, expiry_date,term_cond,coupon_company) values (%s,%s,%s,%s,%s)"
                vals = (user_id, cpn, exp, tnc, company)
                cur.execute(query, vals)
                conn.commit()
                print "Inserted"
                curr_indx = t6
        except ValueError as e:
            pass
        except Exception as e:
            print "Exception freecharge: " + str(e)

    elif 'paytm' in data:
        company = 'paytm'
        try:
            t1 = data.index('Your coupons', 0)
            t1a = data.index('[image:', t1)
            t2 = data.index(']', t1)
            cpn_prefix = data[t1a + 8:t2]
            t3 = data.index('Coupon Code', t2)
            cpn = data[t2 + 1:t3]
            cpn = cpn_prefix + ": " + cpn
            print cpn
            t4 = data.index('Coupon Conditions:', t3)
            t5 = data.index('<http', t4)
            tnc = data[t4 + 18: t5]
            print tnc
            exp = ''
            query = "insert into offer_infos(user_id,title, expiry_date,term_cond,coupon_company) values (%s,%s,%s,%s,%s)"
            vals = (user_id, cpn, exp, tnc, company)
            cur.execute(query, vals)
            conn.commit()
            print "Inserted"
        except Exception as e:
            print 'Exception: ' + str(e)
