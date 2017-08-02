bl_info = {
    "name": "Blender Pip",
    "author": "David",
    "location": "User Preferences",
    "version": (1, 0, 0),
    "blender": (2, 7, 4),
    "description": "Allow easy installation of pip packages",
    "wiki_url": "",
    "category": "Development"
    }

import importlib
from os.path import dirname, basename, isfile

import time
import pprint
import ctypes, sys
import urllib.request
import ast
from subprocess import Popen, PIPE


if "bpy" in globals():
    importlib.reload(bpy)
else:
    import bpy
from bpy.types import Panel, Operator, AddonPreferences
from bpy.props import StringProperty, IntProperty, BoolProperty
from pprint import pprint as pprint

global pip_install
global pip_uninstall


def pip_installed():
        try:
            import pip
        except Exception as e:
            print(e)
            return False
        else:
            return True


def pip_install_mod(module_name):
        import pip
        pm_module_name = 'pip'
        pm_module_path = pip.__file__
        command  = "['install', '"+str(module_name)+"']"
        command = str(command)
        #args = ['install', module_name]
        print(command)
        pprint(dir(bpy.ops.pip_blender))
        bpy.ops.pip_blender.console_dia('INVOKE_DEFAULT', module_name=pm_module_name, command=command, module_path=pm_module_path)

def pip_uninstall_mod(module_name):
        import pip
        pm_module_name = 'pip'
        pm_module_path = pip.__file__
        command  = "['uninstall', '"+str(module_name)+"']"
        #args = ['uninstall', module_name]
        print(command)
        pprint(dir(bpy.ops.pip_blender))
        bpy.ops.pip_blender.console_dia('INVOKE_DEFAULT',module_name=pm_module_name, command=command, module_path=pm_module_path)


def update_unInstPack(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        pprint(prefs['unInstPack'])
        #context.window_manager.unInstPack = prefs['unInstPack']


def update_instPack(self, context):
        prefs = context.user_preferences.addons[__name__].preferences
        pprint(prefs['instPack'])




class BlipPreferences(AddonPreferences):
        context = bpy.context
        bl_idname = __name__
        bl_space_type = 'USER_PREFERENCES'
        bl_region_type = 'WINDOW'
        bl_label = 'Add Pip'
        instPack = StringProperty(name="instPack", update=update_instPack)
        unInstPack = StringProperty(name="unInstPack", update=update_unInstPack)



        def draw(self, context):
                layout = self.layout
                column1 = layout.column()
                if not pip_installed():
                    column1.label(icon="ERROR", text="This will install pip for your blender python which may reduce the stability of your blender installation.  It make require administrator access.  It may download a file from the internet.  It will create a symlink to your modules directory.  Do you wish to continue?")
                    column1.operator( __name__+".install_pip", text='Install Pip')
                else:
                    column1.operator( __name__+".uninstall_pip", text='Unnstall Pip')
                column2 = layout.column()
                row1 = column2.row()
                row1.label(text="Install package here or use pip_install(example_package) in console")
                row2 = column2.row()
                row2.prop(self, "instPack", "Install Package")
                row2.operator( __name__+".install_pip_pkg", text='Install')
                row3 = column2.row()
                row3.label(text="Uninstall package here or use pip_uninstall(example_package) in console")
                row4 = column2.row()
                row4.prop(self, "unInstPack", "Uninstall Package")
                row4.operator( __name__+".uninstall_pip_pkg", text='Uninstall')
                return {'FINISHED'}

        def invoke(self, context, event):
                wm = context.window_manager


class InstallPipPackage(Operator):
        context = bpy.context
        bl_idname = __name__+".install_pip_pkg"
        bl_context = 'user_preferences'
        bl_space_type = 'USER_PREFERENCES'
        bl_label = 'Install Pip Package'
        #unInstPack = StringProperty(name="unInstPack")

        @classmethod
        def poll(cls, context):
                # method called by blender to check if the operator can be run
                return context.scene is not None

        def __init__(self):
                print("Start Install")

        def __del__(self):
                print("End Install")


        def execute(self, context):
                prefs = context.user_preferences.addons[__name__].preferences
                print(vars(prefs))
                instPack = prefs['instPack']
                print(instPack)
                pip_install(instPack)
                mod_name = str(instPack)
                print(mod_name)
                try:
                    mod = __import__(mod_name)
                except Exception as e:
                    print(e)
                    return {'CANCELLED'}
                return {'FINISHED'}

        def invoke(self, context, event):
                print('installpkg invoked')
                return self.execute(context)

class UnnstallPipPackage(Operator):
        context = bpy.context
        bl_idname = __name__+".uninstall_pip_pkg"
        bl_space_type = 'USER_PREFERENCES'
        bl_label = 'Uninstall Pip Package'
        #unInstPack = StringProperty(name="unInstPack")

        @classmethod
        def poll(cls, context):
                # method called by blender to check if the operator can be run
                return context.scene is not None

        def __init__(self):
                print("Start UnInstall Pkg")

        def __del__(self):
                print("End Uninstall Pkg")


        def execute(self, context):
                print('uninstallpkg executed')
                prefs = context.user_preferences.addons[__name__].preferences
                pprint(context.user_preferences.addons['pip_blender'].preferences.instPack)
                unInstPack = prefs['unInstPack']
                pip_uninstall(unInstPack)
                mod_name = str(unInstPack)
                try:
                    mod = __import__(mod_name)
                except Exception as e:
                    print(e)
                    print('mod uninstalled')
                    return {'FINISHED'}
                return {'CANCELLED'}

        def invoke(self, context, event):
                print('uninstallpkg invoked')
                return self.execute(context)

class InstallPipOperator(Operator):
        context = bpy.context
        bl_idname = __name__+".install_pip"
        bl_context = 'user_preferences'
        bl_space_type = 'USER_PREFERENCES'
        bl_label = "Install Pip"


        def install_pip(self):
                print('function install_pip')
                import os.path

                try:
                    from setuptools.command import easy_install
                    bpy.ops.wm.console_dia('INVOKE_DEFAULT',module='easy_install.__file__', command='[\"-U\",\"pip\"]').invoke()
                    if pip_installed():
                            return {'FINISHED'}
                    else:
                            return {'CANCELLED'}

                except Exception as e:
                    print(e)
                    return {'CANCELLED'}


        @classmethod
        def poll(cls, context):
                # method called by blender to check if the operator can be run
                return context.scene is not None

        def __init__(self):
                print("Start Install")

        def __del__(self):
                print("End Uninstall")


        def execute(self, context):
                print('install executed')
                return {'FINISHED'}

        def invoke(self, context, event):
                print('install invoked')
                return self.install_pip()


class UninstallPipOperator(Operator):
    context = bpy.context
    bl_idname = __name__+".uninstall_pip"
    bl_label = "Uninstall Pip"
    bl_space_type = 'USER_PREFERENCES'


    def uninstall_pip(self):
            print('function uninstall_pip')
            print('pip installed')
            import pip
            module_name = pip.__file__
            command = '[\"uninstall\",\"pip\"]'
            bpy.ops.blender_pip.console_dia('INVOKE_DEFAULT',module_name=module_name, command=command)

            try:
                if not pip_installed():
                        print('uninstall finished')
                        return {'FINISHED'}
                else:
                        print('uninstall cancelled')
                        return {'CANCELLED'}

            except Exception as e:
                print(e)
                return {'CANCELLED'}

    @classmethod
    def poll(cls, context):
            # method called by blender to check if the operator can be run
            return context.scene is not None

    def __init__(self):
            print("Start Uninstall")

    def __del__(self):
            print("End Uninstall")

    def execute(self, context):
            print('uninstall executed')
            return {'PASS_THROUGH'}

    def invoke(self, context, event):
            print('uninstall invoked')
            return self.uninstall_pip()



def update_console_in(self, context):
        pprint(dir(bpy.ops.blender_pip.console_dia))

def update_console_out(self, context):
        pprint(dir(bpy.ops.blender_pip.console_dia))

class DialogOperator(bpy.types.Operator):
    context = bpy.context
    bl_idname = __name__+".console_dia"
    bl_label = "Pip Prompter"
    bl_space_type = 'USER_PREFERENCES'
    wm = bpy.context.window_manager
    console_in = bpy.props.StringProperty(name="console_in", update=update_console_in)
    command = bpy.props.StringProperty(name="command")
    console_out = bpy.props.StringProperty(name="console_out")
    console_err = bpy.props.StringProperty(name="console_err")
    module_name = bpy.props.StringProperty(name="module_name")
    module_path = bpy.props.StringProperty(name="module_path")
    args = bpy.props.StringProperty(name="args")

    stdoutold = ''
    stderrold = ''
    stdinold = ''
    process = False



    @classmethod
    def poll(cls, context):
            # method called by blender to check if the operator can be run
            return context.scene is not None

    def __init__(self):
            print("Start Dialog")

    def __del__(self):
            print("End Dialog")


    def invoke(self, context, event):
        self.event = event
        self.context = context
        import sys
        from io import StringIO

        my_buffer = StringIO()

        orig_stdout = sys.stdout
        sys.stdout = my_buffer
        args = ast.literal_eval(self.command)
        pprint(args)
        #module = __import__(self.module_name)
        #module.main(self.command)

        sys.stdin.write('Y')

        sys.stdout = orig_stdout
        print(my_buffer.getvalue())
        return {'FINISHED'}
        #return self.execute(context)

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text=self.console_out)
        col.prop(self, "console_in", "Input")


    def execute(self, context):
        print('Dialog executed')
        self.get_from_console(context)
        self.put_to_console(context, self.console_in)
        self.console_in = ''
        return {'PASS_THROUGH'}

    def put_to_console(self, context, stdin):
        print('Putting to Console')
        print(self.process.returncode)
        if(self.process.returncode is None):
            print('no returncode')
            self.wm.invoke_props_dialog(self, width=500, height=800)
            if(self.console_in is not '' and self.console_in is not self.stdinold):
                self.process.stdin.write(bytes(self.console_in, 'utf-8'))
            self.execute(context)
        else:
            print ('returned')
            return{'FINISHED'}


    def get_from_console(self, context):
        print('Getting From Console')
        cons_out, cons_err = self.process.communicate()
        print('cons_out')
        pprint(cons_out)
        print('cons_err')
        pprint(cons_err)
        if(cons_out):
            print('console out')
            self.console_out = str(cons_out, 'utf-8')
        if(cons_err):
            print('console error')
            self.console_err =str(cons_err, 'utf-8')
        print(self.console_out)
        print(self.console_err)




def register():
        bpy.utils.register_module(__name__)
        global pip_install
        pip_install = pip_install_mod
        global pip_uninstall
        pip_uninstall = pip_uninstall_mod


def unregister():
        bpy.utils.unregister_module(__name__)



if __name__ == '__main__':
    register()
