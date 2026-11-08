import Foundation
import PDFKit
import AppKit
let doc=PDFDocument(url: URL(fileURLWithPath:CommandLine.arguments[1]))!
if CommandLine.arguments.count == 2 {
 for i in 0..<doc.pageCount { print("\n--- PAGE \(i+1) ---\n" + (doc.page(at:i)!.string ?? "")) }
} else {
 let i=Int(CommandLine.arguments[2])!-1
 let page=doc.page(at:i)!
 let img=page.thumbnail(of:NSSize(width:1800,height:2400),for:.mediaBox)
 let rep=NSBitmapImageRep(data:img.tiffRepresentation!)!
 try! rep.representation(using:.png,properties:[:])!.write(to:URL(fileURLWithPath:CommandLine.arguments[3]))
}
