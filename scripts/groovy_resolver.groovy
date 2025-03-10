import groovy.json.JsonSlurper
import groovy.text.SimpleTemplateEngine

def input_expression = args[0]// input_expression
def filename = args[1] // filename with vars
def customVars = new JsonSlurper().parseText(new File(filename).text)
def formula = "\${" + input_expression + "}"
def val =  new SimpleTemplateEngine().createTemplate(formula).make(customVars).toString()

println(val == "true")
