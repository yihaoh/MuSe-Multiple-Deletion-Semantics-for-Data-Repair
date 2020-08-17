// this script is used to control Add/Drop Rules
// <div class="input-group">
//     <label class="input-group-text">Rule</label> 
//     <input type="text" class="form-control input-md">
// </div>
// var schemas = {{ table_schemas | safe }};
// var tables = Object.keys(schemas)

function getFirstNum(s) {
    var res = "";
    for (i = 0; i < s.length; i++) {
        while (s[i] >= '0' && s[i] <= '9' && i < s.length) {
            res += s[i];
            i++;
        }
        if (res != "")
            break;
    }
    return res;
}


function addRuleConstructor(id, detail) {
    // buttons
    buttons = detail.append("div").attr("class", "input-group");
    buttons.append("button").attr("type", "button")
        .attr("class", "btn btn-secondary btn-sm")
        .attr("style", "font-size: large;")
        //.attr("id", id + "-Rule-Add-Table")
        .text("+Table")
        .on("click", function e() {
            var tpid = getFirstNum(this.parentNode.parentNode.id);
            var tID = document.getElementById("Rule-" + tpid + "-Select").childElementCount;
            d3.select("#" + "Rule-" + tpid + "-Select").append("select").attr("id", "Rule-" + tpid + "-Select-" + tID)
                .selectAll("option").data(tables)
                .enter().append("option").text(function (d) { return d; });
        });
    buttons.append("button").attr("type", "button")
        .attr("class", "btn btn-secondary btn-sm")
        .attr("style", "font-size: large;")
        //.attr("id", "Rule-" + id + "-Del-Table")
        .text("-Table")
        .on("click", function e() {
            var tpid = getFirstNum(this.parentNode.parentNode.id);
            rm = document.getElementById("Rule-" + tpid + "-Select");
            if (rm.childElementCount > 2) {
                rm.removeChild(rm.lastChild);
            }
        });

    // buttons that add/delete constraints
    buttons.append("button").attr("type", "button")
        .attr("class", "btn btn-secondary btn-sm")
        .attr("style", "font-size: large;")
        //.attr("id", "Rule-" + id + "-Add-Cons")
        .text("+Constraint")
        .on("click", function e() {
            var tpid = getFirstNum(this.parentNode.parentNode.id);
            var cID = (document.getElementById("Rule-" + id + "-Cons").childElementCount - 2) / 2 + 2;
            var conds = ["AND", "OR", "NOT"];
            d3.select("#" + "Rule-" + tpid + "-Cons").append("select").attr("id", "Rule-" + tpid + "-Cond-" + cID)
                .selectAll("option").data(conds)
                .enter().append("option").text(function (d) { return d; });
            d3.select("#" + "Rule-" + tpid + "-Cons").append("input").attr("id", "Rule-" + tpid + "-Cons-" + cID)
        });

    buttons.append("button").attr("type", "button")
        .attr("class", "btn btn-secondary btn-sm")
        .attr("style", "font-size: large;")
        //.attr("id", "Rule-" + id + "-Del-Cons")
        .text("-Constraint")
        .on("click", function e() {
            var tpid = getFirstNum(this.parentNode.parentNode.id);
            rm = document.getElementById("Rule-" + tpid + "-Cons");
            if (rm.childElementCount > 2) {
                rm.removeChild(rm.lastChild);
                rm.removeChild(rm.lastChild);
            }
        });


    // second line in builder
    second = detail.append("div").attr("class", "input-group");
    second.append("span").attr("class", "input-group-text").text("DELTA_");
    second.append("select").attr("id", "Rule-" + id + "-Delta")
        .on("change", function e() {
            var tpid = getFirstNum(this.id);
            var t = d3.select(this).node().value;
            d3.select("#Rule-" + tpid + "-Select-1").text(t);
        })
        .selectAll("option").data(tables)
        .enter().append("option").text(function (d) { return d; });
    second.append("span").attr("class", "input-group-text").text(":=");

    // third line in builder
    third = detail.append("div").attr("class", "input-group").attr("id", "Rule-" + id + "-Select");
    third.append("span").attr("class", "input-group-text").text("SELECT * FROM ");
    third.append("span").attr("class", "input-group-text")
        .attr("id", "Rule-" + id + "-Select-1")
        .text($("#" + "Rule-" + id + "-Delta").val());
    // add/del takes effect and id in form: id-Rule-Table-tID, add listener to button to add select

    // fourth line in builder
    fourth = detail.append("div").attr("class", "input-group").attr("id", "Rule-" + id + "-Cons");
    fourth.append("span").attr("class", "input-group-text").text("WHERE ");
    fourth.append("input").attr("id", "Rule-" + id + "-Cons-1");
    // add/det takes effect and id in form: id-Rule-Cons-cID, id-Rule-Cond-cID, add listener to button

    detail.append("div").attr("class", "input-group")
        .append("p").attr("id", "Rule-" + id + "-Disp").attr("class", "lead");

    detail.append("input").attr("id", "Rule-" + id).attr("name", "Rule-" + id)
        .attr("readonly", true).attr("type", "hidden");

    function updateRes(c) {
        var m = new Object();
        var m1 = new Object();

        var tpid = getFirstNum(c.id);
        var t = $("#" + "Rule-" + tpid + "-Delta").val();
        var res = "DELETE * FROM " + t + " WHERE " + t + ".* IN (SELECT " + t + ".* FROM " + t;
        m[t] = 1;

        // check if first cons need to be in EXISTS
        var select = 2;
        var tp = d3.select("#Rule-" + tpid + "-Select-" + select).node();
        while (tp) {
            if (m.hasOwnProperty(tp.value)) {
                //res += ", " + tp.value + " " + tp.value + m[tp.value]++;
                m[tp.value]++;
            }
            else {
                //res += ", " + tp.value;
                m[tp.value] = 1;
            }
            select++;
            tp = d3.select("#Rule-" + tpid + "-Select-" + select).node();
        }

        var select = 2;
        tp = d3.select("#Rule-" + tpid + "-Select-" + select).node();
        while (tp) {
            if (!m1.hasOwnProperty(tp.value)) {
                m1[tp.value] = 1;
            }
            if (m.hasOwnProperty(tp.value) && m[tp.value] == 1) {
                res += ", " + tp.value;
            }
            else if (m.hasOwnProperty(tp.value) && m[tp.value] > 1) {
                res += ", " + tp.value + " " + tp.value + m1[tp.value]++;
            }
            select++;
            tp = d3.select("#Rule-" + tpid + "-Select-" + select).node();
        }

        var cons = 2;
        tp = d3.select("#Rule-" + tpid + "-Cons-1").node();
        if (!tp || tp.value == "") {
            res += ");";
            d3.select("#" + "Rule-" + tpid + "-Disp").text(res);
            d3.select("#" + "Rule-" + tpid).attr("value", res);
            return;
        }
        
        res += " WHERE " + tp.value;
        
        // constraint and table goes in parallel
        var tp1 = d3.select("#Rule-" + tpid + "-Cond-" + cons).node();
        var tp2 = d3.select("#Rule-" + tpid + "-Cons-" + cons).node();

        while (tp1 && tp2) {
            res += " " + tp1.value + " " + tp2.value;
            cons++;
            tp1 = d3.select("#Rule-" + tpid + "-Cond-" + cons).node();
            tp2 = d3.select("#Rule-" + tpid + "-Cons-" + cons).node();
        }

        // if (cons == 2)
        //     res = res.substring(0, res.length - 13);
        res += ");";

        //console.log(res);
        
        d3.select("#" + "Rule-" + tpid + "-Disp").text(res);
        d3.select("#" + "Rule-" + tpid).attr("value", res);
        console.log("RC update gets called");
    }

    updateRes(detail.node());

    detail.on("change", function e() { updateRes(this); });
    $("#Rule-" + id + "-Select").on("DOMSubtreeModified", function e() { updateRes(this); });
    //detail.node().on("DOMSubtreeModified", function e() { updateRes(this); });

}

// add functional dependency for delta rule
function addFD(id, detail) {

    buttons = detail.append("div").attr("class", "input-group");
    buttons.append("button").attr("type", "button")
        .attr("class", "btn btn-secondary btn-sm")
        .attr("style", "font-size: large;")
        //.attr("id", id + "-Rule-Add-Table")
        .text("+Attribute")
        .on("click", function e() {
            
            var tpid = getFirstNum(this.parentNode.parentNode.id);
            var tp = document.getElementById("Rule-" + tpid + "-FDLeft");
            var cnt = tp.childElementCount - 1;
            tp.removeChild(tp.lastChild);
            d3.select("#" + "Rule-" + id + "-FDLeft").append("select").attr("id", "Rule-" + tpid + "-Attr" + cnt)
                .selectAll("option").data(schemas[$("#" + "Rule-" + tpid + "-Delta").val()])
                .enter().append("option").text(function (d) { return d; });
            d3.select("#" + "Rule-" + tpid + "-FDLeft").append("span").attr("class", "input-group-text").text(" => ");

        });
    buttons.append("button").attr("type", "button")
        .attr("class", "btn btn-secondary btn-sm")
        .attr("style", "font-size: large;")
        //.attr("id", "Rule-" + id + "-Del-Table")
        .text("-Attribute")
        .on("click", function e() {
            var tpid = getFirstNum(this.parentNode.parentNode.id);
            rm = document.getElementById("Rule-" + tpid + "-FDLeft");
            if (rm.childElementCount > 3) {
                rm.removeChild(rm.lastChild);
                rm.removeChild(rm.lastChild);
                d3.select("#" + "Rule-" + tpid + "-FDLeft").append("span").attr("class", "input-group-text").text(" => ");
            }
        });

    //FD = detail.append("div").attr("class", "input-group");
    FDLeft = detail.append("div").attr("id", "Rule-" + id + "-FDLeft").attr("class", "input-group");
    FDLeft.append("select").attr("id", "Rule-" + id + "-Delta")
        .on("change", function e() {
            var tpid = getFirstNum(this.id); 

            var t = d3.select(this).node().value;
            d3.select("#Rule-" + tpid + "-Default").text(t);

            var cnt = 1;
            var tp = d3.select("#Rule-" + tpid + "-Attr" + cnt);
            while (tp.node() != null) {
                d3.select("#Rule-" + tpid + "-Attr" + cnt).selectAll("option").data([]).exit().remove();
                tp.selectAll("option").data(schemas[$("#" + "Rule-" + tpid + "-Delta").val()])
                    .enter().append("option").text(function (d) { return d; });
                cnt += 1;
                tp = d3.select("#Rule-" + tpid + "-Attr" + cnt);
            }
            d3.select("#Rule-" + tpid + "-Right").selectAll("option").data([]).exit().remove();
            d3.select("#Rule-" + tpid + "-Right").selectAll("option").data(schemas[$("#" + "Rule-" + tpid + "-Delta").val()])
                .enter().append("option").text(function (d) { return d; });


        })
        .selectAll("option").data(tables)
        .enter().append("option").text(function (d) { return d; });
    FDLeft.append("select").attr("id", "Rule-" + id + "-Attr1")
        .selectAll("option").data(schemas[$("#" + "Rule-" + id + "-Delta").val()])
        .enter().append("option").text(function (d) { return d; });
    FDLeft.append("span").attr("class", "input-group-text").text(" => ");

    FDRight = detail.append("div").attr("class", "input-group");

    FDRight.append("span").attr("class", "input-group-text")
        .attr("id", "Rule-" + id + "-Default")
        .text($("#" + "Rule-" + id + "-Delta").val());
    FDRight.append("select").attr("id", "Rule-" + id + "-Right")
        .selectAll("option").data(schemas[$("#" + "Rule-" + id + "-Delta").val()])
        .enter().append("option").text(function (d) { return d; });

    detail.append("br");
    detail.append("div").attr("class", "input-group")
        .append("p").attr("id", "Rule-" + id + "-Disp").attr("class", "lead");

    detail.append("input").attr("id", "Rule-" + id).attr("name", "Rule-" + id)
        .attr("readonly", true).attr("type", "hidden");

    function updateRes(c) {
        //console.log(c.id)
        var tpid = getFirstNum(c.id); 
        var table = $("#" + "Rule-" + tpid + "-Delta").val();
        var res = "DELETE * FROM " + table + " WHERE " + table + ".* IN (SELECT " + table + "1.* FROM " +
                    table + " " + table + "1, " + table + " " + table + "2 WHERE ";

        var cnt = 1;
        var tp = d3.select("#Rule-" + tpid + "-Attr" + cnt).node();
        res += table + "1." + tp.value + "=" + table + "2." + tp.value;
        cnt += 1;
        tp = d3.select("#Rule-" + tpid + "-Attr" + cnt).node();
        while (tp) {
            res += " AND " + table + "1." + tp.value + "=" + table + "2." + tp.value;
            cnt += 1;
            tp = d3.select("#Rule-" + tpid + "-Attr" + cnt).node();
        }

        tp = d3.select("#Rule-" + tpid + "-Right").node();
        res += " AND " + table + "1." + tp.value + "<>" + table + "2." + tp.value + ");";

        // console.log(res);
        // console.log(d3.select("#" + "Rule-" + tpid + "-Disp"))
        d3.select("#" + "Rule-" + tpid + "-Disp").text(res);
        d3.select("#" + "Rule-" + tpid).attr("value", res);
        console.log("FD update gets called");
    }
    updateRes(detail.node());
    detail.on("change", function e() { updateRes(this); });

}

function addFK(id, detail) {
    FK = detail.append("div").attr("class", "input-group");
    FK.append("select").attr("id", "Rule-" + id + "-Table1")
        .on("change", function e() {
            d3.select("#Rule-" + id + "-Attr1").selectAll("option").data([]).exit().remove();
            d3.select("#Rule-" + id + "-Attr1").selectAll("option").data(schemas[$("#" + "Rule-" + id + "-Table1").val()])
                .enter().append("option").text(function (d) { return d; });
        })
        .selectAll("option").data(tables)
        .enter().append("option").text(function (d) { return d; });
    FK.append("select").attr("id", "Rule-" + id + "-Attr1")
        .selectAll("option").data(schemas[$("#" + "Rule-" + id + "-Table1").val()])
        .enter().append("option").text(function (d) { return d; });
    FK.append("span").attr("class", "input-group-text").text(" => ");
    FK.append("select").attr("id", "Rule-" + id + "-Table2")
        .on("change", function e() {
            d3.select("#Rule-" + id + "-Attr2").selectAll("option").data([]).exit().remove();
            d3.select("#Rule-" + id + "-Attr2").selectAll("option").data(schemas[$("#" + "Rule-" + id + "-Table2").val()])
                .enter().append("option").text(function (d) { return d; });
        })
        .selectAll("option").data(tables)
        .enter().append("option").text(function (d) { return d; });
    FK.append("select").attr("id", "Rule-" + id + "-Attr2")
        .selectAll("option").data(schemas[$("#" + "Rule-" + id + "-Table2").val()])
        .enter().append("option").text(function (d) { return d; });

    // result display and hidden input for data passing
    detail.append("div").attr("class", "input-group")
        .append("p").attr("id", "Rule-" + id + "-Disp").attr("class", "lead");

    detail.append("input").attr("id", "Rule-" + id).attr("name", "Rule-" + id)
        .attr("readonly", true).attr("type", "hidden");

    // update results
    function updateRes(c) {
        var tpid = getFirstNum(c.id);
        var tb1 = $("#" + "Rule-" + tpid + "-Table1").val();
        var tb2 = $("#" + "Rule-" + tpid + "-Table2").val();
        var at1 = $("#" + "Rule-" + tpid + "-Attr1").val();
        var at2 = $("#" + "Rule-" + tpid + "-Attr2").val();
        // var res = "delta_" + tb2 + ":=SELECT * FROM " + tb2 + ", " + "delta_" + tb1 +
        //     " WHERE " + tb2 + "." + at2 + "=" + tb1 + "." + at1 + ";";
        var res = "DELETE * FROM " + tb2 + " WHERE " + tb2 + ".* IN (SELECT " + tb2 + ".* FROM " + tb2 +
                  ", " + tb1 + " WHERE " + tb1 + "." + at1 + "=" + tb2 + "." + at2 + ");";

        d3.select("#" + "Rule-" + tpid + "-Disp").text(res);
        d3.select("#" + "Rule-" + tpid).attr("value", res);
        console.log("FK update gets called", res);
    }
    updateRes(detail.node());
    detail.on("change", function e() { updateRes(this); });
}

function addRule() {
    ruleNum = document.getElementById("delta-rule").childElementCount;
    elem = d3.select('#delta-rule');
    detail = elem.append("div")
        .attr("class", "card card-cascade narrower")
        .attr("style", "background-color: rgba(11, 181, 211, 0.3)")
        .append("div").attr("class", "px-4 mb-1 mt-2");

    detail.append("div").attr("class", "input-group").append("h3").text("Rule " + ruleNum.toString());
    // first line in builder, Rule Type
    ruleTy = ["Rule Constructor", "Functional Dependency", "Foreign Key"];
    first = detail.append("div").attr("class", "input-group-prepend");
    first.append("span").attr("class", "input-group-text").text("Rule Type:");
    first.append("select").attr("id", "Rule-" + ruleNum + "-Type")
        .attr("class", "form-control").attr("style", "width:auto;")
        .on("change", function e() {
            var t = d3.select(this).node().value;
            var tpid = getFirstNum(d3.select(this).node().id);
            
            var list = document.getElementById("container-" + tpid);
            while (list.hasChildNodes()) {  
                list.removeChild(list.firstChild);
            }

            $('#container-' + tpid).off();

            // addFD/addFK/addRC all have (int id, d3 selector detail)
            if (t == "Functional Dependency") {
                addFD(tpid, d3.select("#container-" + tpid));
            } else if (t == "Foreign Key") {
                addFK(tpid, d3.select("#container-" + tpid));
            } else {  // rule constructor
                addRuleConstructor(tpid, d3.select("#container-" + tpid));
            }
        })
        .selectAll("option").data(ruleTy)
        .enter().append("option").text(function (d) { return d; });
    //addFD(ruleNum, detail);
    d = detail.append("div").attr("id", "container-" + ruleNum);
    addRuleConstructor(ruleNum, d);

    // div = elem.append("div")
    // div.attr("class", "input-group");
    // div.append("label").attr("class", "input-group-text").text("Rule " + ruleNum.toString());
    // div.append("input")
    //     .attr("class", "form-control input-md")
    //     .attr("type", "text")
    //     .attr("id", "rule-" + ruleNum.toString())
    //     .attr("name", "rule-" + ruleNum.toString());
}
function delRule() {
    rm = document.getElementById('delta-rule');
    if (rm.childElementCount > 1) {
        rm.removeChild(rm.lastChild);
    }
}
d3.select('#add-rule').on("click", addRule);
d3.select('#del-rule').on("click", delRule);
