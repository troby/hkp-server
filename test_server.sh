#!/bin/ksh

curl -v http://127.0.0.1:8080/ 2>&1 |grep 'Welcome' >/dev/null
if [ $? == 0 ]
then
  echo "test index ...                        OK"
else
  echo "test index ...                      FAIL"
fi
curl -v 'http://127.0.0.1:8080/pks/lookup?op=get&search=C218525819F78451' 2>&1 |grep 'Dingledine' >/dev/null
if [ $? == 0 ]
then
  echo "test lookup ...                       OK"
else
  echo "test lookup ...                     FAIL"
fi
curl -v 'http://127.0.0.1:8080/pks/lookup?op=get&search=ABC' 2>&1 |grep 'Key not found' >/dev/null
if [ $? == 0 ]
then
  echo "test missing key ...                  OK"
else
  echo "test missing key ...                FAIL"
fi
curl -v 'http://127.0.0.1:8080/test_not_found' 2>&1 |grep 'NOT FOUND' >/dev/null
if [ $? == 0 ]
then
  echo "test 404 ...                          OK"
else
  echo "test 404 ...                        FAIL"
fi
