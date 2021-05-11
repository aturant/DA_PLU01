from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict

import sqlite3

router_4 = APIRouter()


##########################################################
@router_4.on_event("shutdown")
@router_4.on_event("startup")
def make_connection():
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    if hasattr('router_4', 'conn'):
        router_4.conn.close()
        print("connection closed")
    else:
        router_4.conn = sqlite3.connect('northwind.db', check_same_thread=False)
        router_4.conn.text_factory = lambda b: b.decode(errors="ignore").strip()
        router_4.conn.row_factory = dict_factory
        print("connection created")


router_4.sql_dict = dict()


####
def extract_end_point_from_request(request: Request):
    my_url = request.url.path[1::].lower()
    try:
        my_url = my_url[0:my_url.index("/"):]
    except ValueError:
        pass
    finally:
        return my_url


def extract_sql_from_endpoint(request: Request):
    end_point = extract_end_point_from_request(request)
    sql = router_4.sql_dict[end_point]
    return sql, end_point


def extract_data_from_endpoint(request: Request, QueryParamDict: Optional[Dict] = {}):
    sql, end_point = extract_sql_from_endpoint(request)
    rows = router_4.conn.execute(sql, QueryParamDict).fetchall()
    return sql, end_point, rows


# router_4.sql_dict["4"]="select
#                             P.ProductID id, p.ProductName name,c.CategoryName category,
#                             S.CompanyName supplier
#                         FROM
#                         Products P
#                         left join Suppliers S using(SupplierID)
#                         left join Categories C using(CategoryID)
#                         order by id"


# Na pierwszy ogień stwórz dwa endpointy /categories oraz /customers. Oba endpointy mają być obsługiwane przez metodę
# GET, zwracać kod HTTP 200 oraz dane mają być posortowane po kolumnie id. Endpoint /categories ma zwracać rekordy z
# tabeli Categories w następującym formacie:
#
# {
#     "categories": [
#          {"id": 1, "name": "Beverages"},
#          [...]
#      ]
# }
# gdzie id to jest kolumna CategoryID, zaś name to CategoryName.
# Endpoint /customers ma zwracać rekordy z tabeli Customers w następującym formacie:
# {
#     "customers": [
#         {
#             "id": "ALFKI",
#             "name": "Alfreds Futterkiste",
#             "full_address":  "Obere Str. 57 12209 Berlin Germany",
#         },
#         [...]
#      ]
# }
# gdzie id to jest kolumna CustomerID, name to kolumna CompanyName,
# zaś full_address to są dane połączone z czterech kolumn w kolejności:
# Address, PostalCode, City oraz Country oddzielone spacją.
router_4.sql_dict["categories"] = \
    "SELECT	CategoryID id,CategoryName name " \
    "FROM Categories order by id;"
router_4.sql_dict["customers"] = \
    'SELECT ' \
    'CustomerID id, CompanyName name, Address || " " || PostalCode || " " || City || " " || Country full_address ' \
    'FROM Customers order by id'


@router_4.get("/categories")
@router_4.get("/customers")
def main(request: Request):
    sql, end_point, rows = extract_data_from_endpoint(request)
    response = {end_point: rows}
    return JSONResponse(response)


# ############################### 4.2 Stwórz kolejny endpoint /products/[id]. Endpoint ma być obsługiwany przez
# metodę GET. Ma przyjmować id oraz zwracać dane rekordu z tabeli Products pod podanym id. Endpoint standardowo ma
# zwracać kod HTTP 200 lub HTTP 404 gdy rekord o podanym id nie istnieje. Zwrócona odpowiedź ma być jsonem w
# następującym formacie:
#
# {"id": 1, "name": "Chai"}
# gdzie id to jest kolumna ProductID, zaś name to ProductName.

router_4.sql_dict["products"] = \
    "SELECT ProductID id, ProductName name " \
    "FROM Products where ProductID=:ProductID"


@router_4.get("/products/{id}")
def main(id: int, request: Request):
    QryParamDict = {"ProductID": id}
    sql, end_point, rows = extract_data_from_endpoint(request, QryParamDict)

    if not len(rows):
        raise HTTPException(404, "ID does not exist")
    return JSONResponse(*rows, status_code=200)


################################ 4.3
# Stwórz endpoint /employees, obsługiwany przez metodę GET, ma zwracać defaultowo kod HTTP 200
# oraz ma pobierać dane z tabeli Employees. Dane defaultowo mają być posortowane po kolumnie id.
# Ponad to endpoint ma obsługiwać query parametry: limit, offset oraz order.
# Parametry limit oraz offset będą intami, zaś order będzie stringiem z nazwą kolumny po której
# należy posortować dane rosnąco. Dopuszczalne wartości dla parametru order to first_name, last_name, city.
# Gdyby parametr order miał inną wartość, należy zwrócić kod HTTP 400.
# Dane z ednpointu mają być zwrócone w postaci jsona w następującym formacie:
#
# {
#     "employees": [
#         {"id":1,"last_name":"Davolio","first_name":"Nancy","city":"Seattle"},
#         [...]
#    ]
# }
# gdzie id to jest kolumna EmployeeID, last_name to LastName, first_name to FirstName, zaś city to City.
router_4.sql_dict["employees"] = \
    "select EmployeeID id, LastName last_name, FirstName first_name, City city " \
    "from Employees e order by :order limit :limit offset :offset"


@router_4.get("/employees", status_code=200)
def main(limit: int, offset: int, order: str, request: Request):
    if order not in {'first_name', 'last_name', 'city'}:
        raise HTTPException(status_code=400, detail='order is not recognized')
    QryParamDict = {"limit": limit, "offset": offset, "order": order}
    sql, end_point, rows = extract_data_from_endpoint(request, QryParamDict)

    response = {end_point: rows}
    return JSONResponse(response)
# 4.5
