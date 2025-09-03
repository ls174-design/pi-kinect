#!/usr/bin/env python3
"""
Diagnostic test for the fixed camera viewer
"""

import sys
import os

def test_fixed_viewer():
    """Test the fixed camera viewer"""
    print("🧪 Testing fixed camera viewer...")
    
    try:
        # Test file access
        viewer_file = "windows_camera_viewer_fixed.py"
        if not os.path.exists(viewer_file):
            print(f"❌ File not found: {viewer_file}")
            return False
        
        # Test file reading
        with open(viewer_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 100:
            print(f"✅ File exists and readable: {len(content)} characters")
        else:
            print(f"❌ File seems empty: {len(content)} characters")
            return False
        
        # Test import
        import windows_camera_viewer_fixed
        print("✅ Import successful")
        
        # Test basic functionality
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        try:
            viewer = windows_camera_viewer_fixed.CameraViewer(root)
            print("✅ Camera viewer object created successfully")
            root.destroy()
            return True
        except Exception as e:
            print(f"❌ Camera viewer creation failed: {e}")
            root.destroy()
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🔍 Fixed Camera Viewer Diagnostic")
    print("=" * 40)
    
    if test_fixed_viewer():
        print("\n🎉 Fixed camera viewer is working correctly!")
        print("💡 You can now use: test_fixed_viewer.bat")
    else:
        print("\n❌ Fixed camera viewer still has issues")
        print("💡 Check the error messages above")

if __name__ == '__main__':
    main()
