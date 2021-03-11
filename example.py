
import npyscreen


class EmployeeForm(npyscreen.Form):

    def create(self):
        self.myName = self.add(npyscreen.TitleText, name='Name')
        self.myDepartment = self.add(npyscreen.TitleSelectOne, scroll_exit=True, max_height=3, name='Department', values=[
                                     'Science and Environment', 'Social Sciences and Business', 'People and Technology', 'Communication and Arts'])
        self.myDate = self.add(npyscreen.TitleDateCombo, name='Date Employed')

    def afterEditing(self):
        # Update values on next form
        self.parentApp.switchForm('CONFIRM')
        self.parentApp.getForm('CONFIRM').wgName.value = self.myName.value
        self.parentApp.getForm('CONFIRM').wgDept.value = self.myDepartment.values[0]
        self.parentApp.getForm('CONFIRM').wgEmp.value  = self.myDate.value


class EmployeeConfirmForm(npyscreen.ActionForm):

    def create(self):
        self.add(npyscreen.FixedText, value="Is this correct?", editable=False)
        self.wgName = self.add(npyscreen.TitleText, name="Name:",     editable=False)
        self.wgDept = self.add(npyscreen.TitleText, name="Dept:",     editable=False)
        self.wgEmp  = self.add(npyscreen.TitleText, name="Employed:", editable=False)

    def on_ok(self):
        self.parentApp.setNextForm(None)

    def on_cancel(self):
        self.parentApp.switchFormPrevious()


class myApp(npyscreen.NPSAppManaged):

    def onStart(self):
        self.addForm('MAIN', EmployeeForm, name='Employee Entry')
        self.addForm('CONFIRM', EmployeeConfirmForm, name='Employee Confirmation')


if __name__ == '__main__':
    TestApp = myApp().run()